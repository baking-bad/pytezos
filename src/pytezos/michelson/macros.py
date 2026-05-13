import functools
import re
from collections import namedtuple
from typing import Any
from typing import List
from typing import Tuple

from pytezos.michelson.tags import prim_tags

COMPARE = {'prim': 'COMPARE'}
UNIT = {'prim': 'UNIT'}
FAILWITH = {'prim': 'FAILWITH'}
DUP = {'prim': 'DUP'}
SWAP = {'prim': 'SWAP'}
CAR = {'prim': 'CAR'}
CDR = {'prim': 'CDR'}
CAR__ = {'prim': 'CAR', 'annots': ['@%%']}
CDR__ = {'prim': 'CDR', 'annots': ['@%%']}
DROP = {'prim': 'DROP'}
FAIL = [[UNIT, FAILWITH]]

macros: List[Any] = []

PxrNode = namedtuple('PxrNode', ['depth', 'annots', 'args', 'is_root'])


def macro(regexp):
    def register_macro(func):
        macros.append((re.compile(regexp), func))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return register_macro


def seq(instr=None) -> list:
    if instr is None:
        return []
    elif isinstance(instr, list):
        return instr
    else:
        return [instr]


def expand_macro(prim, annots, args, internal=False):
    """Expands Michelson macro.

    :param prim: macro name
    :param annots: annotations (optional)
    :param args: arguments (optional)
    :param internal: this function is called during another macro expansion
    :returns: Code sequence (Micheline expression)
    """
    assert isinstance(annots, list)
    assert isinstance(args, list)
    if prim in prim_tags:
        return expr(prim=prim, annots=annots, args=args)

    for regexp, handler in macros:
        groups = regexp.findall(prim)
        if groups:
            assert len(groups) == 1
            res = handler(groups[0], annots, args)
            return res if internal else seq(res)

    raise AssertionError(f'unknown primitive `{prim}`')


def get_field_annots(annots):
    return list(filter(lambda x: isinstance(x, str) and x[0] == '%', annots))


def get_var_annots(annots):
    return list(filter(lambda x: isinstance(x, str) and x[0] == '@', annots))


def skip_nones(array):
    return list(filter(lambda x: x is not None, array))


def expr(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v}


def dip_n(instr, depth=1):
    if depth <= 0:
        return instr
    elif depth == 1:
        return expr(
            prim='DIP',
            args=[seq(instr)],
        )
    else:
        return expr(
            prim='DIP',
            args=[{'int': str(depth)}, seq(instr)],
        )


@macro(r'^CMP(EQ|NEQ|LT|GT|LE|GE)$')
def expand_cmpx(prim, annots, args) -> list:
    assert not args
    return [
        COMPARE,
        expr(prim=prim, annots=annots),
    ]


@macro(r'^IF(EQ|NEQ|LT|GT|LE|GE)$')
def expand_ifx(prim, annots, args) -> list:
    assert len(args) == 2
    return [
        expr(prim=prim, annots=annots),
        expr(prim='IF', args=args),
    ]


@macro(r'^IFCMP(EQ|NEQ|LT|GT|LE|GE)$')
def expand_ifcmpx(prim, annots, args) -> list:
    assert len(args) == 2
    return [
        [COMPARE, expr(prim=prim, annots=annots)],
        expr(prim='IF', args=args),
    ]


@macro(r'^FAIL$')
def expand_fail(prim, annots, args) -> list:
    assert not annots
    assert not args
    return [
        UNIT,
        FAILWITH,
    ]


@macro(r'^ASSERT$')
def expand_assert(prim, annots, args) -> dict:
    assert not annots
    assert not args
    return expr(
        prim='IF',
        args=[[], FAIL],
    )


@macro(r'^ASSERT_(EQ|NEQ|LT|LE|GT|GE)$')
def expand_assert_x(prim, annots, args) -> list:
    assert not args
    assert not annots  # TODO: ask why
    return expand_ifx(
        prim,
        annots=[],
        args=[[], FAIL],
    )


@macro(r'^ASSERT_CMP(EQ|NEQ|LT|LE|GT|GE)$')
def expand_assert_cmpx(prim, annots, args) -> list:
    assert not args
    assert not annots  # TODO: ask why
    return expand_ifcmpx(
        prim,
        annots=[],
        args=[[], FAIL],
    )


@macro(r'^ASSERT_NONE$')
def expand_assert_none(prim, annots, args) -> dict:
    assert not annots
    assert not args
    return expr(
        prim='IF_NONE',
        args=[[], FAIL],
    )


@macro('^ASSERT_SOME$')
def expand_assert_some(prim, annots, args) -> dict:
    assert not args
    return expr(
        prim='IF_NONE',
        args=[FAIL, [expr(prim='RENAME', annots=annots)]],
    )


@macro('^ASSERT_LEFT$')
def expand_assert_left(prim, annots, args) -> dict:
    assert not args
    return expr(
        prim='IF_LEFT',
        args=[[expr(prim='RENAME', annots=annots)], FAIL],
    )


@macro('^ASSERT_RIGHT$')
def expand_assert_right(prim, annots, args) -> dict:
    assert not args
    return expr(
        prim='IF_LEFT',
        args=[FAIL, [expr(prim='RENAME', annots=annots)]],
    )


@macro(r'^D(II+)P$')
def expand_dixp(prim, annots, args) -> dict:
    assert not annots
    assert len(args) == 1
    return dip_n(args, depth=len(prim))


@macro(r'^D(UU+)P$')
def expand_duxp(prim, annots, args) -> dict:
    assert not args
    depth = len(prim)
    return expr(
        prim='DUP',
        annots=annots,
        args=[{'int': str(depth)}],
    )


def build_pxr_tree(pxr_macro, pxr_annots) -> PxrNode:
    def parse(prim, annots, depth=0, is_root=False):
        letter, prim = prim[0], prim[1:]
        if letter == 'P':
            dip_depth = depth
            left, l_annot, prim, annots, depth = parse(prim, annots, depth)
            right, r_annot, prim, annots, depth = parse(prim, annots, depth)
            return (
                PxrNode(
                    dip_depth,
                    [l_annot, r_annot],
                    [left, right],
                    is_root,
                ),
                None,
                prim,
                annots,
                depth,
            )
        else:
            annot, annots = (annots[0], annots[1:]) if annots else (None, [])
            return letter, annot, prim, annots, depth + 1

    root, _, _, _, _ = parse(pxr_macro, pxr_annots, is_root=True)
    return root


def traverse_pxr_tree(prim, annots, produce):
    res = []

    def walk(node):
        if isinstance(node, PxrNode):
            res.insert(0, dip_n(produce(node), depth=node.depth))
            _ = list(map(walk, node.args))

    walk(build_pxr_tree(prim, annots))
    return res


@macro(r'^P[PAI]{3,}R$')
def expand_pxr(prim, annots, args) -> list:
    def produce(node: PxrNode):
        pair_annots = [node.annots[0] or '%', node.annots[1]] if any(node.annots) else []
        if node.is_root:
            pair_annots.extend(get_var_annots(annots))
        return expr(prim='PAIR', annots=skip_nones(pair_annots))

    assert not args
    return traverse_pxr_tree(prim, get_field_annots(annots), produce)


@macro(r'^UN(P[PAI]{3,}R)$')
def expand_unpxr(prim, annots, args) -> list:
    def produce(node: PxrNode):
        return [expr(prim='UNPAIR', annots=skip_nones(node.annots))]

    assert not args
    return list(reversed(traverse_pxr_tree(prim, annots, produce)))


def expand_cxr(prim, annots) -> list:
    return seq(expand_macro(prim=f'C{prim}R', annots=annots, args=[], internal=True))


@macro(r'^CA([AD]+)R$')
def expand_caxr(prim, annots, args) -> list:
    assert not args
    return [
        CAR,
        *expand_cxr(prim, annots),
    ]


@macro(r'^CD([AD]+)R$')
def expand_cdxr(prim, annots, args) -> list:
    assert not args
    return [
        CDR,
        *expand_cxr(prim, annots),
    ]


@macro(r'^IF_SOME$')
def expand_if_some(prim, annots, args) -> dict:
    assert not annots
    assert len(args) == 2
    return expr(
        prim='IF_NONE',
        args=list(reversed(args)),
    )


@macro(r'^IF_RIGHT$')
def expand_if_right(prim, annots, args) -> dict:
    assert not annots
    assert len(args) == 2
    return expr(
        prim='IF_LEFT',
        args=list(reversed(args)),
    )


@macro(r'^SET_CAR$')
def expand_set_car(prim, annots, args) -> list:
    assert not args
    return [
        SWAP,
        expr(
            prim='UPDATE',
            args=[{'int': '1'}],
            annots=annots,
        ),
    ]


@macro(r'^SET_CDR$')
def expand_set_cdr(prim, annots, args) -> list:
    assert not args
    return [
        SWAP,
        expr(
            prim='UPDATE',
            args=[{'int': '2'}],
            annots=annots,
        ),
    ]


def expand_set_cxr(prim, annots):
    set_cxr = expand_macro(
        prim=f'SET_C{prim}R',
        annots=get_field_annots(annots),
        args=[],
        internal=True,
    )
    pair = expr(
        prim='PAIR',
        annots=['%@', '%@'] + get_var_annots(annots),
    )
    return set_cxr, pair


@macro(r'^SET_CA([AD]+)R$')
def expand_set_caxr(prim, annots, args) -> list:
    assert not args
    set_cxr, pair = expand_set_cxr(prim, annots)
    return [
        DUP,
        dip_n([CAR__, set_cxr]),
        CDR__,
        SWAP,
        pair,
    ]


@macro(r'^SET_CD([AD]+)R$')
def expand_set_cdxr(prim, annots, args) -> list:
    assert not args
    set_cxr, pair = expand_set_cxr(prim, annots)
    return [
        DUP,
        dip_n([CDR__, set_cxr]),
        CAR__,
        pair,
    ]


def get_map_cxr_annots(annots) -> Tuple[str, list]:
    field_annots = get_field_annots(annots)
    if field_annots:
        assert len(field_annots) == 1
        return field_annots[0], [f'@{field_annots[0][1:]}']
    else:
        return '%', []


@macro(r'^MAP_CAR$')
def expand_map_car(prim, annots, args) -> list:
    car_annot, var_annots = get_map_cxr_annots(annots)
    return [
        DUP,
        CDR__,
        dip_n(
            [
                expr(
                    prim='CAR',
                    annots=var_annots,
                ),
                *args,
            ]
        ),
        SWAP,
        expr(
            prim='PAIR',
            annots=[car_annot, '%@'],
        ),
    ]


@macro(r'^MAP_CDR$')
def expand_map_cdr(prim, annots, args) -> list:
    cdr_annot, var_annots = get_map_cxr_annots(annots)
    return [
        DUP,
        expr(prim='CDR', annots=var_annots),
        *args,
        SWAP,
        CAR__,
        expr(
            prim='PAIR',
            annots=['%@', cdr_annot],
        ),
    ]


def expand_map_cxr(prim, annots, args):
    set_cxr = expand_macro(
        prim=f'MAP_C{prim}R',
        annots=get_field_annots(annots),
        args=args,
        internal=True,
    )
    pair = expr(
        prim='PAIR',
        annots=['%@', '%@'] + get_var_annots(annots),
    )
    return set_cxr, pair


@macro(r'^MAP_CA([AD]+)R$')
def expand_map_caxr(prim, annots, args) -> list:
    map_cxr, pair = expand_map_cxr(prim, annots, args)
    return [
        DUP,
        dip_n([CAR__, map_cxr]),
        CDR__,
        SWAP,
        pair,
    ]


@macro(r'^MAP_CD([AD]+)R$')
def expand_map_cdxr(prim, annots, args) -> list:
    map_cxr, pair = expand_map_cxr(prim, annots, args)
    return [
        DUP,
        dip_n([CDR__, map_cxr]),
        CAR__,
        pair,
    ]
