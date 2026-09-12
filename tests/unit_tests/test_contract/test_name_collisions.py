import warnings
from unittest import TestCase

from pytezos import ContractInterface
from pytezos.contract.data import ContractData
from pytezos.contract.entrypoint import ContractEntrypoint
from pytezos.contract.interface import ContractTokenMetadataProxy
from pytezos.contract.view import ContractView
from pytezos.michelson.sections import ViewSection
from pytezos.michelson.types.base import MichelsonType

KEEP_STORAGE = 'code { CDR; NIL operation; PAIR }'


def load(source: str) -> ContractInterface:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return ContractInterface.from_michelson(source)


class NameCollisionsTest(TestCase):
    """Entrypoints and views named like ContractInterface attributes (issue #314)"""

    def test_view_token_metadata(self):
        ci = load(f'parameter nat; storage nat; {KEEP_STORAGE}; view "token_metadata" nat nat {{ CAR }}')
        self.assertEqual(1, ci.view.token_metadata(1).onchain_view(storage=7))
        self.assertIs(ContractTokenMetadataProxy, type(ci.token_metadata))
        self.assertNotIn('token_metadata', vars(ci))

    def test_entrypoint_and_view_share_name(self):
        ci = load(f'''
            parameter (or (nat %balance_of) (unit %default));
            storage nat;
            {KEEP_STORAGE};
            view "balance_of" nat nat {{ UNPAIR; ADD }};
            ''')
        self.assertIsInstance(ci.balance_of, ContractEntrypoint)
        self.assertIs(ci.balance_of, ci.entrypoint.balance_of)
        self.assertIs(ci.entrypoint.balance_of, ci.entrypoint['balance_of'])
        self.assertIsInstance(ci.view.balance_of, ContractView)
        self.assertEqual(10, ci.view.balance_of(3).onchain_view(storage=7))
        self.assertEqual(0, ci.entrypoint.balance_of(3).interpret(storage=0).storage)

    def test_entrypoint_metadata(self):
        ci = load(f'parameter (or (nat %metadata) (unit %default)); storage nat; {KEEP_STORAGE}')
        self.assertEqual(0, ci.entrypoint.metadata(7).interpret(storage=0).storage)
        self.assertNotIn('metadata', vars(ci))

    def test_storage_name(self):
        ci = load(f'''
            parameter (or (nat %storage) (unit %default));
            storage nat;
            {KEEP_STORAGE};
            view "storage" unit nat {{ CDR }};
            ''')
        self.assertIs(ContractData, type(ci.storage))
        self.assertEqual(0, ci.entrypoint.storage(5).interpret(storage=0).storage)
        self.assertEqual(7, ci.view.storage().onchain_view(storage=7))

    def test_reserved_attribute_names(self):
        names = ['call', 'parameter', 'key', 'address', 'code', 'context', 'shell', 'program', 'using', 'default']
        ci = load(f"""
            parameter (or (or (or (nat %call) (nat %parameter)) (or (nat %key) (nat %address)))
                          (or (or (nat %code) (nat %context)) (or (or (nat %shell) (nat %program)) (or (nat %using) (nat %default)))));
            storage nat;
            {KEEP_STORAGE};
            """)
        for name in names:
            self.assertEqual(name, ci.entrypoint[name].entrypoint, name)
            self.assertEqual(name, getattr(ci.entrypoint, name).entrypoint, name)
        self.assertEqual('root', ci.parameter.entrypoint)
        self.assertEqual(0, ci.entrypoint.key(1).interpret(storage=0).storage)
        self.assertEqual(sorted([*names, 'root']), sorted(ci.entrypoint))

    def test_root_entrypoint_reserved_name(self):
        ci = load(f'parameter (nat %storage); storage nat; {KEEP_STORAGE}')
        self.assertIs(ci.parameter, ci.entrypoint.storage)

    def test_entrypoint_token_metadata(self):
        source = f'parameter (or (nat %token_metadata) (unit %default)); storage nat; {KEEP_STORAGE}'
        with warnings.catch_warnings():
            warnings.simplefilter('error')  # legacy TZIP-12 entrypoint stays silent, as in 3.19
            ci = ContractInterface.from_michelson(source)
        self.assertEqual('token_metadata', ci.entrypoint.token_metadata.entrypoint)
        self.assertIs(ContractTokenMetadataProxy, type(ci.token_metadata))

    def test_collision_warning(self):
        source = f'''
            parameter (or (nat %storage) (nat %balance_of));
            storage nat;
            {KEEP_STORAGE};
            view "balance_of" nat nat {{ CAR }};
        '''
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            ContractInterface.from_michelson(source)
        messages = [str(w.message) for w in caught]
        self.assertEqual(
            [
                '`.storage` is reserved, use `.entrypoint.storage` instead',
                '`.balance_of` is reserved, use `.view.balance_of` instead',
            ],
            messages,
        )

    def test_no_collision_keeps_old_surface(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            ci = ContractInterface.from_michelson(
                f'parameter (or (nat %mint) (unit %default)); storage nat; {KEEP_STORAGE}; view "bar" nat nat {{ CAR }}'
            )
        self.assertEqual([], caught)
        self.assertIs(ci.mint, ci.entrypoint.mint)
        self.assertIs(ci.bar, ci.view.bar)
        self.assertTrue(issubclass(ci.entrypoints['mint'], MichelsonType))
        self.assertTrue(issubclass(ci.views['bar'], ViewSection))

    def test_view_shadowed_by_root_entrypoint(self):
        source = f'parameter (nat %default); storage nat; {KEEP_STORAGE}; view "default" nat nat {{ CAR }}'
        with self.assertWarnsRegex(UserWarning, r'`\.default` is reserved, use `\.view\.default`'):
            ci = ContractInterface.from_michelson(source)
        self.assertIs(ci.default, ci.entrypoint.default)
        self.assertIs(ci.parameter, ci.entrypoint.default)
        self.assertEqual(3, ci.view.default(3).onchain_view(storage=0))

    def test_repr_and_dir(self):
        ci = load(f'''
            parameter (or (nat %storage) (nat %balance_of));
            storage nat;
            {KEEP_STORAGE};
            view "balance_of" nat nat {{ CAR }};
            view "fine" nat nat {{ CAR }};
            ''')
        text = repr(ci)
        self.assertIn('.entrypoint.storage()', text)
        self.assertIn('\n.balance_of()\n', text)
        self.assertIn('.view.balance_of()', text)
        self.assertIn('\n.fine()\n', text)
        self.assertIn('.entrypoint\t# entrypoints by name', text)

        self.assertIn('balance_of', dir(ci.view))
        self.assertIn('storage', dir(ci.entrypoint))
        self.assertIn('\n.balance_of()\n.fine()', repr(ci.view))
        self.assertIn('balance_of', ci.view)
        self.assertNotIn('nope', ci.view)

        with self.assertRaisesRegex(AttributeError, 'unknown view `nope`'):
            _ = ci.view.nope
        self.assertFalse(hasattr(ci.view, 'nope'))
        with self.assertRaises(KeyError):
            _ = ci.entrypoint['nope']
        with self.assertRaisesRegex(AttributeError, 'unexpected entrypoint nope'):
            _ = ci.nope

    def test_docstrings(self):
        ci = load(
            f'parameter (or (nat %storage) (unit %default)); storage nat; {KEEP_STORAGE}; view "storage" unit nat {{ CDR }}'
        )
        self.assertIn('$storage', ci.entrypoint.storage.__doc__)
        self.assertIn('unit', ci.view.storage.__doc__)

    def test_non_identifier_entrypoint_name(self):
        ci = load(f'parameter (or (nat %foo.bar) (unit %default)); storage nat; {KEEP_STORAGE}')
        self.assertEqual(0, ci.entrypoint['foo.bar'](1).interpret(storage=0).storage)
        self.assertEqual('foo.bar', ci.entrypoint['foo.bar'].entrypoint)
