import pendulum
from decimal import Decimal
from collections import namedtuple

from pytezos.encoding import base58_encode

Schema = namedtuple('Schema', ['type_map', 'collapsed_tree'])
Nested = namedtuple('Nested', ['prim', 'args'])
Route = namedtuple('Route', ['path', 'value'])


def get_flat_nested(nested: Nested):
    flat_args = list()
    for arg in nested.args:
        if isinstance(arg, Nested) and arg.prim == nested.prim:
            flat_args.extend(get_flat_nested(arg))
        else:
            flat_args.append(arg)
    return flat_args


def get_route_terminal(route: Route):
    if isinstance(route.value, Route):
        return get_route_terminal(route.value)
    return route


def make_dict(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v}


def decode_literal(node, prim):
    core_type, value = next(iter(node.items()))
    if prim in ['int', 'nat']:
        return int(value)
    if prim == 'timestamp':
        if core_type == 'int':
            return pendulum.from_timestamp(int(value))
        else:
            return pendulum.parse(value)
    if prim == 'mutez':
        return Decimal(value) / 10 ** 6
    if prim == 'bool':
        return value == 'True'
    if prim == 'address' and core_type == 'bytes':
        prefix = {'0000': b'tz1', '0001': b'tz2', '0002': b'tz3'}  # TODO: check it's ttr
        return base58_encode(bytes.fromhex(value[4:]), prefix[value[:4]]).decode()
    return value


def encode_literal(value, prim, binary=False):
    if prim in ['int', 'nat']:
        core_type = 'int'
        value = str(value)
    elif prim == 'timestamp':
        core_type = 'string'
        if isinstance(value, int):
            value = pendulum.from_timestamp(value)
        if isinstance(value, pendulum.DateTime):
            value = value.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif prim == 'mutez':
        core_type = 'int'
        if isinstance(value, Decimal):
            value = int(value * 10 ** 6)
        if isinstance(value, int):
            value = str(value)
    elif prim == 'bool':
        core_type = 'prim'
        value = 'True' if value else 'False'
    elif prim == 'bytes':
        core_type = 'bytes'
    else:
        core_type = 'string'
        value = str(value)

    return {core_type: value}


def build_schema(code) -> Schema:
    type_map = dict()

    def get_annotation(x, prefix, default=None):
        return next((a[1:] for a in x.get('annots', []) if a[0] == prefix), default)

    def parse_node(node, path='0', parent_prim=None):
        if node['prim'] in ['storage', 'parameter']:
            return parse_node(node['args'][0])

        type_map[path] = dict(prim=node['prim'])
        typename = get_annotation(node, ':')
        name = get_annotation(node, '%', typename)

        args = [
            parse_node(arg, path=path + str(i), parent_prim=node['prim'])
            for i, arg in enumerate(node.get('args', []))
        ]

        if node['prim'] in ['pair', 'or']:
            res = Nested(node['prim'], args)
            if typename or parent_prim != node['prim']:
                args = get_flat_nested(res)
                type_map[path]['children'] = list(map(lambda x: x['path'], args))
                props = list(map(lambda x: x.get('name'), args))
                if all(props):
                    type_map[path]['props'] = props
            else:
                return res
        elif node['prim'] == 'option' and not name:
            name = args[0].get('name')

        return make_dict(
            prim=node['prim'],
            path=path,
            args=args,
            name=name,
        )

    collapsed_tree = parse_node(code)
    return Schema(type_map, collapsed_tree)


def get_json_path(schema: Schema, path):
    type_info = schema.type_map[path[0]]
    json_path = list()
    for i in path[1:]:
        index = int(i)
        if type_info.get('props'):
            json_path.append(type_info['props'][index])
        else:
            json_path.append(i)
        type_info = schema.type_map[type_info['children'][index]]
    return '/'.join(json_path)


def decode_data(data, schema: Schema, annotations=True, literals=True, root='0'):
    def decode_node(node, path='0'):
        type_info = schema.type_map.get(path, {})
        if isinstance(node, dict):
            args = (
                decode_node(arg, path + str(i))
                for i, arg in enumerate(node.get('args', []))
            )
            if node.get('prim') == 'Pair':
                res = Nested(type_info['prim'], list(args))
                if type_info.get('children'):
                    res = tuple(get_flat_nested(res))
                    if type_info.get('props') and annotations:
                        res = dict(zip(type_info['props'], res))

            elif node.get('prim') in ['Left', 'Right']:
                arg_path = path + {'Left': '0', 'Right': '1'}[node['prim']]
                res = Route(arg_path, decode_node(node['args'][0], arg_path))
                if type_info.get('children'):
                    terminal = get_route_terminal(res)
                    if type_info.get('props') and annotations:
                        index = type_info['children'].index(terminal.path)
                        res = {type_info['props'][index]: terminal.value}
                    else:
                        res = terminal.value

            elif node.get('prim') == 'Elt':
                res = list(args)
            elif node.get('prim') == 'Some':
                res = next(iter(args))
            elif node.get('prim') == 'None':
                res = None
            elif literals:
                res = decode_literal(node, type_info['prim'])
            else:
                _, res = next(iter(node.items()))

        elif isinstance(node, list):
            if type_info['prim'] in ['map', 'big_map']:
                res = dict(decode_node(item, path) for item in node)
            else:
                args = (decode_node(item, path + '0') for item in node)
                if type_info['prim'] == 'set':
                    res = set(args)
                elif type_info['prim'] == 'list':
                    res = list(args)
                else:
                    raise ValueError(node, type_info)
        else:
            raise ValueError(node, type_info)

        return res

    return decode_node(data, root)


def build_value_map(data, schema: Schema, root='0') -> dict:
    value_map = dict()

    def find_root(node):
        if node['path'] == root:
            return node
        for arg in node.get('args', []):
            res = find_root(arg)
            if res:
                return res
        return None

    def parse_value(node, node_info, is_element=False):
        if node_info['prim'] == 'pair':
            values = node
            if isinstance(node, dict):  # props
                values = [node[arg['name']] for arg in node_info['args']]
            for i, arg_info in enumerate(node_info['args']):
                parse_value(values[i], arg_info, is_element)

        elif node_info['prim'] in ['map', 'big_map']:
            value_map[node_info['path']] = len(node)
            for key, value in node.items():
                parse_value(key, node_info['args'][0], True)
                parse_value(value, node_info['args'][1], True)

        elif node_info['prim'] in ['set', 'list']:
            value_map[node_info['path']] = len(node)
            for value in node:
                parse_value(value, node_info['args'][0], True)

        elif node_info['prim'] == 'or':
            key, value = next(iter(node.items()))
            if isinstance(key, str):
                key, arg_info = next(
                    (i, arg)
                    for i, arg in enumerate(node_info['args'])
                    if arg['name'] == key
                )
            else:
                arg_info = node_info['args'][key]
            parse_value(value, arg_info, is_element)

        elif node_info['prim'] == 'michelson':
            parse_value(node, node_info['args'][0], is_element)

        elif node_info['prim'] == 'option':
            parse_value(node, node_info['args'][0], is_element)

        elif is_element:
            value_map[node_info['path']] = value_map.get(node_info['path'], []) + [node]
        else:
            value_map[node_info['path']] = node

    root_node = find_root(schema.collapsed_tree)
    parse_value(data, root_node)
    return value_map


def encode_data(data, schema: Schema, binary=False, root='0'):
    value_map = build_value_map(data, schema, root=root)

    def get_value(path, index=None):
        if path not in value_map:
            raise KeyError(path)
        value = value_map[path]
        if index is not None:
            return value[index]
        return value

    def encode_node(path='0', index=None):
        type_info = schema.type_map[path]
        if type_info['prim'] == 'pair':
            return dict(
                prim='Pair',
                args=list(map(lambda x: encode_node(path + x, index), '01'))
            )
        elif type_info['prim'] in ['map', 'big_map']:
            return [
                dict(
                    prim='Elt',
                    args=[encode_node(path + '0', i), encode_node(path + '1', i)]
                )
                for i in range(get_value(path))
            ]
        elif type_info['prim'] in ['set', 'list']:
            return [
                encode_node(path + '0', i)
                for i in range(get_value(path))
            ]
        elif type_info['prim'] == 'or':
            for i in [0, 1]:
                try:
                    return dict(
                        prim={0: 'Left', 1: 'Right'}[i],
                        args=[encode_node(path + str(i), index)]
                    )
                except KeyError:
                    continue
        elif type_info['prim'] == 'option':
            arg = encode_node(path + '0', index)
            if arg is None:
                return dict(prim='None')
            else:
                return dict(prim='Some', args=[arg])

        return encode_literal(
            value=get_value(path, index),
            prim=type_info['prim'],
            binary=binary
        )

    return encode_node(root)


def decode_schema(schema: Schema):
    def decode_node(node):
        if node['prim'] == 'or':
            return {
                arg.get('name', str(i)): decode_node(arg)
                for i, arg in enumerate(node['args'])
            }
        if node['prim'] == 'pair':
            args = list(map(lambda x: (x.get('name'), decode_node(x)), node['args']))
            names, values = zip(*args)
            return dict(args) if all(names) else values
        if node['prim'] == 'set':
            return {decode_node(node['args'][0])}
        if node['prim'] == 'list':
            return [decode_node(node['args'][0])]
        if node['prim'] in {'map', 'big_map'}:
            return {decode_node(node['args'][0]): decode_node(node['args'][1])}
        if node['prim'] == 'option':
            return decode_node(node['args'][0])

        return f'#{node["prim"]}'

    return decode_node(schema.collapsed_tree)