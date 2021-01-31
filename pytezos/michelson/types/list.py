from typing import Tuple, Generator, List, Type
from pprint import pformat

from pytezos.michelson.types.base import MichelsonType
from pytezos.context.base import NodeContext


class ListType(MichelsonType, prim='list', args_len=1):

    def __init__(self, items: List[MichelsonType]):
        super(ListType, self).__init__()
        self.items = items

    def __repr__(self):
        return pformat([repr(x) for x in self.items])

    def __len__(self):
        return len(self.items)

    def __iter__(self) -> Generator[MichelsonType, None, None]:
        yield from self.items

    @staticmethod
    def empty(item_type: Type[MichelsonType]):
        cls = ListType.create_type(args=[item_type])
        return cls(items=[])

    @staticmethod
    def from_items(items: List[MichelsonType]):
        assert len(items) > 0, 'cannot instantiate from empty list'
        item_type = type(items[0])
        for item in items[1:]:
            item_type.assert_equal_types(type(item))
        cls = ListType.create_type(args=[item_type])
        return cls(items)

    @classmethod
    def generate_pydoc(cls, definitions: List[Tuple[str, str]], inferred_name=None):
        name = cls.field_name or cls.type_name or inferred_name
        arg_doc = cls.args[0].generate_pydoc(definitions, inferred_name=f'{name}_item' if name else None)
        return f'[ {arg_doc}, ... ]'

    @classmethod
    def dummy(cls, context: NodeContext) -> 'ListType':
        return cls([])

    @classmethod
    def from_micheline_value(cls, val_expr: list) -> 'ListType':
        assert isinstance(val_expr, list), f'expected list, got {type(val_expr).__name__}'
        items = list(map(cls.args[0].from_micheline_value, val_expr))
        return cls(items)

    @classmethod
    def from_python_object(cls, py_obj) -> 'ListType':
        assert isinstance(py_obj, list), f'expected list, got {type(py_obj).__name__}'
        items = list(map(cls.args[0].from_python_object, py_obj))
        return cls(items)

    def to_micheline_value(self, mode='readable', lazy_diff=False):
        return list(map(lambda x: x.to_micheline_value(mode=mode, lazy_diff=lazy_diff), self))

    def to_python_object(self, try_unpack=False, lazy_diff=False):
        return list(map(lambda x: x.to_python_object(try_unpack=try_unpack, lazy_diff=lazy_diff), self))

    def merge_lazy_diff(self, lazy_diff: List[dict]) -> 'MichelsonType':
        items = [item.merge_lazy_diff(lazy_diff) for item in self]
        return type(self)(items)

    def aggregate_lazy_diff(self, lazy_diff: List[dict], mode='readable'):
        for item in self:
            item.aggregate_lazy_diff(lazy_diff, mode=mode)

    def attach_context(self, context: NodeContext, big_map_copy=False):
        for item in self:
            item.attach_context(context, big_map_copy=big_map_copy)

    def split_head(self) -> Tuple[MichelsonType, 'ListType']:
        assert len(self) > 0, f'cannot split empty list'
        head = self.items[0]
        tail = type(self)(self.items[1:])
        return head, tail

    def prepend(self, item: MichelsonType) -> 'ListType':
        self.args[0].assert_equal_types(type(item))
        return type(self)([item] + self.items)

    def __getitem__(self, idx: int) -> MichelsonType:
        assert isinstance(idx, int), f'expected int, got {type(idx).__name__}'
        assert idx < len(self), f'index out of bounds: {idx} >= {len(self)}'
        return self.items[idx]
