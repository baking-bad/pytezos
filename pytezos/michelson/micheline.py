from typing import Dict
from datetime import datetime
from os.path import join, dirname, basename
from decimal import Decimal
from collections import namedtuple, defaultdict
from functools import lru_cache

from pytezos.encoding import parse_address, parse_public_key, forge_public_key, forge_address
from pytezos.michelson.forge import prim_tags
from pytezos.michelson.formatter import micheline_to_michelson
from pytezos.michelson.grammar import MichelsonParser
from pytezos.repl.parser import parse_expression

Nested = namedtuple('Nested', ['prim', 'args'])
Schema = namedtuple('Schema', ['metadata', 'bin_types', 'bin_names', 'json_to_bin'])
BigMapSchema = namedtuple('BigMapSchema', ['bin_to_id', 'id_to_bin'])
meaningful_types = ['key', 'key_hash', 'signature', 'timestamp', 'address']


@lru_cache(maxsize=None)
def michelson_parser():
    return MichelsonParser()


class TypedDict(dict):
    __key_type__ = str

    def __getitem__(self, item):
        return super(TypedDict, self).__getitem__(self.__key_type__(item))

    def __setitem__(self, key, value):
        return super(TypedDict, self).__setitem__(self.__key_type__(key), value)

    @staticmethod
    def make(key_type):
        return type(f'{key_type.__name__.capitalize()}Dict', (TypedDict,), {'__key_type__': key_type})


def skip_nones(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


def is_micheline(value):
    if isinstance(value, list):
        def get_prim(x):
            return x.get('prim') if isinstance(x, dict) else None
        return set(map(get_prim, value)) == {'parameter', 'storage', 'code'}
    elif isinstance(value, dict):
        primitives = list(prim_tags.keys())
        return any(map(lambda x: x in value, ['prim', 'args', 'annots', *primitives]))
    else:
        return False


def decode_literal(node, prim):
    core_type, value = next(iter(node.items()))
    if prim in ['int', 'nat']:
        return int(value)
    elif prim == 'timestamp':
        if core_type == 'int':
            return int(value)
        else:
            return value
    elif prim == 'mutez':
        return Decimal(value) / 10 ** 6
    elif prim == 'bool':
        return value == 'True'
    elif prim in ['address', 'key_hash', 'contract']:
        if core_type == 'bytes':
            return parse_address(bytes.fromhex(value))
        else:
            return value
    elif prim == 'key':
        if core_type == 'bytes':
            return parse_public_key(bytes.fromhex(value))
        else:
            return value
    return value


def decode_comparable(node, bin_types: dict, bin_path):
    if bin_types[bin_path] in ['tuple', 'namedtuple', 'pair']:
        res = list()
        for idx in [0, 1]:
            arg = decode_comparable(node['args'][idx], bin_types, bin_path + str(idx))
            if isinstance(arg, tuple):
                res.extend(list(arg))
            else:
                res.append(arg)
        return tuple(res)
    else:
        return decode_literal(node, bin_types[bin_path])


def encode_literal(value, prim, binary=False):
    core_type = 'string'
    if prim in ['int', 'nat']:
        core_type = 'int'
    elif prim == 'timestamp':
        if isinstance(value, int):
            core_type = 'int'
        elif isinstance(value, datetime):
            value = value.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif prim == 'mutez':
        core_type = 'int'
        if isinstance(value, Decimal):
            value = int(value * 10 ** 6)
    elif prim == 'bool':
        core_type = 'prim'
        value = 'True' if value else 'False'
    elif prim == 'bytes':
        if isinstance(value, bytes):
            value = value.hex()
        core_type = 'bytes'
    elif binary:
        if prim == 'key':
            value = forge_public_key(value).hex()
            core_type = 'bytes'
        elif prim in ['address', 'contract', 'key_hash']:
            value = forge_address(value, tz_only=prim == 'key_hash').hex()
            core_type = 'bytes'

    return {core_type: str(value)}


def get_flat_nested(nested: Nested):
    flat_args = list()
    for arg in nested.args:
        if isinstance(arg, Nested) and arg.prim == nested.prim:
            flat_args.extend(get_flat_nested(arg))
        else:
            flat_args.append(arg)
    return flat_args


def collapse_micheline(code) -> dict:
    metadata = dict()

    def get_annotation(x, prefix, default=None):
        return next((a[1:] for a in x.get('annots', []) if a[0] == prefix), default)

    def parse_node(node, path='0', parent_prim=None, entry=None):
        if node['prim'] in ['storage', 'parameter']:
            return parse_node(node['args'][0])

        fieldname = get_annotation(node, '%')
        typename = get_annotation(node, ':')

        metadata[path] = skip_nones(
            prim=node['prim'],
            typename=typename,
            fieldname=fieldname,
            entry=entry
        )

        if node['prim'] == 'option':
            return parse_node(
                node=node['args'][0],
                path=path + '0',
                parent_prim=parent_prim,
                entry=fieldname
            )
        elif node['prim'] in ['lambda', 'contract']:
            metadata[path]['parameter'] = micheline_to_michelson(node['args'][0], inline=True)
            return dict(path=path, args=[])  # stop there

        args = [
            parse_node(arg, path=path + str(i), parent_prim=node['prim'])
            for i, arg in enumerate(node.get('args', []))
        ]

        if node['prim'] in ['pair', 'or']:
            res = Nested(node['prim'], args)
            is_struct = node['prim'] == 'pair' and (typename or fieldname or entry)
            if is_struct or parent_prim != node['prim']:
                args = get_flat_nested(res)
            else:
                return res

        if args:
            metadata[path]['args'] = list(map(lambda x: x['path'], args))

        return dict(path=path, args=args)

    parse_node(code)
    return metadata


def build_maps(metadata: dict):
    bin_types = {k: v['prim'] for k, v in metadata.items()}
    bin_names, json_to_bin = {}, {}

    def is_unit(bin_path):
        node = metadata[bin_path]
        return node.get('prim') == 'unit'

    def get_union_names(node):
        names = []
        for i, arg_path in enumerate(node['args']):
            arg = metadata[arg_path]
            name = arg.get('entry', arg.get('fieldname', arg.get('typename')))
            if name:
                name = name.replace('_Liq_entry_', '')
            else:
                name = f'entrypoint_{i}'
            names.append(name)
        return names

    def get_tuple_names(node):
        names, unnamed = [], True
        for i, arg_path in enumerate(node['args']):
            arg = metadata[arg_path]
            name = arg.get('typename', arg.get('fieldname', arg.get('entry')))
            if name:
                unnamed = False
            else:
                name = f'@{arg["prim"]}_{i}'
            names.append(name)
        return names, unnamed

    def parse_node(bin_path='0', json_path='/'):
        node = metadata[bin_path]

        if node['prim'] in ['list', 'set']:
            parse_node(node['args'][0], join(json_path, '{}'))

        elif node['prim'] in ['map', 'big_map']:
            parse_node(node['args'][1], join(json_path, '{}'))

        elif node['prim'] == 'or':
            names = get_union_names(node)

            if all(map(is_unit, node['args'])):
                bin_types[bin_path] = 'enum'
                for i, arg_path in enumerate(node['args']):
                    parse_node(arg_path, join(json_path, bin_types[arg_path]))
                    bin_types[arg_path] = names[i]
                    bin_names[arg_path] = names[i]
            else:
                bin_types[bin_path] = 'router'
                for i, arg_path in enumerate(node['args']):
                    parse_node(arg_path, join(json_path, names[i]))
                    bin_names[arg_path] = names[i]

        elif node['prim'] == 'pair':
            names, unnamed = get_tuple_names(node)
            bin_types[bin_path] = 'tuple' if unnamed else 'namedtuple'
            for i, arg_path in enumerate(node['args']):
                parse_node(arg_path, join(json_path, str(i) if unnamed else names[i]))
                bin_names[arg_path] = None if unnamed else names[i]

        json_to_bin[json_path] = bin_path

    parse_node()
    return bin_types, bin_names, json_to_bin


def parse_micheline(val_expr, type_expr, schema: Schema, bin_root='0'):
    def flatten_args(args):
        assert isinstance(args, list) or isinstance(args, tuple), f'iterable expected, got {args}'
        res = list()
        for arg in args:
            if isinstance(arg, list) or isinstance(arg, tuple):
                res.extend(flatten_args(arg))
            else:
                res.append(arg)
        return res

    def decode_selector(val_node, type_node, val, type_path):
        bin_type = schema.bin_types[type_path]
        if bin_type == 'map':
            return dict(val)
        elif bin_type == 'big_map' and isinstance(val_node, list):
            return dict(val)
        elif bin_type == 'pair':
            return tuple(flatten_args(val))
        elif bin_type == 'or':
            arg_path = type_path + {'Left': '0', 'Right': '1'}[val_node['prim']]
            is_leaf = schema.metadata[arg_path]['prim'] != 'or'
            return {schema.bin_names[arg_path]: val[0]} if is_leaf else val[0]
        elif bin_type == 'router':
            return val[0]
        elif bin_type == 'tuple':
            return tuple(flatten_args(val))
        elif bin_type == 'namedtuple':
            names = list(map(lambda x: schema.bin_names[x], schema.metadata[type_path]['args']))
            return dict(zip(names, flatten_args(val)))
        elif bin_type == 'enum':
            return next(iter(val[0]))
        elif bin_type == 'unit':
            return None
        else:
            return val

    if type_expr['prim'] in ['storage', 'parameters']:
        type_expr = type_expr['args'][0]

    return parse_expression(val_expr, type_expr, decode_selector, bin_root)


def parse_json(data, schema: Schema, json_root='/'):
    bin_values = defaultdict(dict)  # type: Dict[str, dict]

    def parse_entry(bin_path, index):
        for i in range(len(bin_path) - 1, 0, -1):
            lpath = bin_path[:i]
            if schema.bin_types[lpath] in ['or', 'router', 'enum']:
                bin_values[lpath][index] = bin_path[i]
            elif schema.bin_types[lpath] in ['list', 'set', 'map', 'big_map']:
                return

    def parse_comparable(key, bin_path, index):
        if schema.bin_types[bin_path] == 'pair':
            assert isinstance(key, tuple), f'tuple expected, got {key}'
            for i, arg_path in enumerate(schema.metadata[bin_path]['args']):
                assert i < len(key), f'not enough elements in tuple {key}'
                bin_values[arg_path][index] = key[i]
        else:
            bin_values[bin_path][index] = key

    def parse_node(node, json_path='/', index='0'):
        bin_path = schema.json_to_bin[json_path]
        bin_type = schema.bin_types[bin_path]

        if isinstance(node, dict):
            if bin_type in ['map', 'big_map']:
                bin_values[bin_path][index] = len(node)
                parse_entry(bin_path, index)
                for i, (key, value) in enumerate(node.items()):
                    parse_comparable(key, bin_path=bin_path + '0', index=f'{index}:{i}')
                    parse_node(value, json_path=join(json_path, '{}'), index=f'{index}:{i}')

            elif bin_type in ['pair', 'or', 'namedtuple', 'router']:
                for key, value in node.items():
                    parse_node(value, json_path=join(json_path, key), index=index)
            else:
                assert False, (node, json_path)

        elif isinstance(node, list):
            if bin_type in ['list', 'set']:
                bin_values[bin_path][index] = len(node)
                parse_entry(bin_path, index)
                for i, value in enumerate(node):
                    parse_node(value, json_path=join(json_path, '{}'), index=f'{index}:{i}')

            elif bin_type in ['pair', 'tuple']:
                for i, value in enumerate(node):
                    parse_node(value, json_path=join(json_path, str(i)), index=index)

            elif bin_type == 'lambda':
                bin_values[bin_path][index] = node

            elif bin_type == 'or':
                assert False, (node, bin_path)  # must be at least lr encoded
        else:
            if bin_type == 'enum':
                parse_node(node, json_path=join(json_path, node), index=index)
            else:
                bin_values[bin_path][index] = node
                parse_entry(bin_path, index)

    parse_node(data, json_path=json_root)
    return dict(bin_values)


def make_micheline(bin_values: dict, bin_types: dict, bin_root='0', binary=False):

    def get_length(bin_path, index):
        try:
            length = bin_values[bin_path][index]
        except KeyError:
            length = 0  # TODO: make sure there is an option ahead
        return length

    def encode_node(bin_path, index='0'):
        bin_type = bin_types[bin_path]

        if bin_type in ['pair', 'tuple', 'namedtuple']:
            return dict(
                prim='Pair',
                args=list(map(lambda x: encode_node(bin_path + x, index), '01'))
            )
        elif bin_type in ['map', 'big_map']:
            length = get_length(bin_path, index)
            return [
                dict(
                    prim='Elt',
                    args=[encode_node(bin_path + '0', f'{index}:{i}'),
                          encode_node(bin_path + '1', f'{index}:{i}')]
                )
                for i in range(length)
            ]
        elif bin_type in ['set', 'list']:
            length = get_length(bin_path, index)
            return [
                encode_node(bin_path + '0', f'{index}:{i}')
                for i in range(length)
            ]
        elif bin_type in ['or', 'router', 'enum']:
            entry = bin_values[bin_path][index]
            return dict(
                prim={'0': 'Left', '1': 'Right'}[entry],
                args=[encode_node(bin_path + entry, index)]
            )
        elif bin_type == 'option':
            try:
                value = encode_node(bin_path + '0', index)
                if value:
                    return dict(prim='Some', args=[value])
                else:
                    return dict(prim='None')
            except KeyError:
                return dict(prim='None')
        elif bin_type == 'lambda':
            return michelson_to_micheline(bin_values[bin_path][index])
        elif bin_type == 'unit':
            return dict(prim='Unit')
        else:
            value = bin_values[bin_path][index]
            if value == bin_type:
                return dict(prim='Unit')
            elif value is None:
                return None
            else:
                return encode_literal(value, bin_type, binary)

    return encode_node(bin_root)


def make_default(bin_types: dict, root='0'):

    def encode_node(bin_path):
        bin_type = bin_types[bin_path]
        if bin_type == 'option':
            return dict(prim='None')
        elif bin_type in ['pair', 'tuple', 'namedtuple']:
            return dict(
                prim='Pair',
                args=list(map(lambda x: encode_node(bin_path + x), '01'))
            )
        elif bin_type in ['map', 'big_map', 'set', 'list']:
            return []
        elif bin_type in ['int', 'nat', 'mutez', 'timestamp']:
            return {'int': '0'}
        elif bin_type in ['string', 'bytes']:
            return {'string': ''}
        elif bin_type == 'bool':
            return {'prim': 'False'}
        elif bin_type == 'unit':
            return {'prim': 'Unit'}
        else:
            raise ValueError(f'Cannot create default value for `{bin_type}` at `{bin_path}`')

    return encode_node(root)


def michelson_to_micheline(data, parser=None):
    """
    Converts michelson source text into Micheline expression
    :param data: Michelson string
    :param parser: custom Michelson parser
    :return: Micheline expression
    """
    if parser is None:
        parser = michelson_parser()
    if data[0] == '(' and data[-1] == ')':
        data = data[1:-1]
    return parser.parse(data)
