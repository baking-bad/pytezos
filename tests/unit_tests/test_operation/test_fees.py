from typing import Any
from typing import Dict
from typing import List
from unittest import TestCase

from pytezos.operation.fees import DEFAULT_CONSTANTS
from pytezos.operation.fees import DEFAULT_TRANSACTION_GAS_LIMIT
from pytezos.operation.fees import DEFAULT_TRANSACTION_STORAGE_LIMIT
from pytezos.operation.fees import calculate_fee
from pytezos.operation.fees import default_fee
from pytezos.operation.fees import default_gas_limit
from pytezos.operation.fees import default_storage_limit


class FeesTest(TestCase):
    def setUp(self) -> None:
        self.content = {
            "kind": "transaction",
            "source": "tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx",
            "fee": "404",
            "counter": "1",
            "gas_limit": "1527",
            "storage_limit": "0",
            "amount": "42000000",
            "destination": "tz1gjaF81ZRRvdzjobyfVNsAeSC6PScjfQwN",
        }

    def test_calculate_fee(self) -> None:
        # Arrange
        consumed_gas = 94
        extra_size = 7
        reserve = 19
        expected_fee = 190

        # Act
        fee = calculate_fee(self.content, consumed_gas, extra_size, reserve)

        # Assert
        self.assertEqual(expected_fee, fee)

    def test_default_fee(self) -> None:
        # Arrange
        expected_fee = 574

        # Act
        fee = default_fee(self.content)

        # Assert
        self.assertEqual(expected_fee, fee)

    def test_default_gas_and_storage_limit(self) -> None:
        # Arrange
        node_gas_limit = 88888
        node_storage_limit = 66666
        node_constants = {
            'hard_gas_limit_per_operation': node_gas_limit,
            'hard_storage_limit_per_operation': node_storage_limit,
        }
        testmap: Dict[str, List[Any]] = {
            'tz_no_constants': [
                'tz',
                None,
                DEFAULT_TRANSACTION_GAS_LIMIT,
                DEFAULT_TRANSACTION_STORAGE_LIMIT,
            ],
            'tz_constants': [
                'tz',
                node_constants,
                DEFAULT_TRANSACTION_GAS_LIMIT,
                DEFAULT_TRANSACTION_STORAGE_LIMIT,
            ],
            'KT_no_constants': [
                'KT',
                None,
                DEFAULT_CONSTANTS['hard_gas_limit_per_operation'],
                DEFAULT_CONSTANTS['hard_storage_limit_per_operation'],
            ],
            'KT_constants': [
                'KT',
                node_constants,
                node_gas_limit,
                node_storage_limit,
            ],
        }

        for name, data in testmap.items():
            dest_prefix, constants, expected_gas_limit, expected_storage_limit = data
            with self.subTest(name):
                # Act
                self.content['destination'] = dest_prefix + self.content['destination'][2:]
                gas_limit = default_gas_limit(self.content, constants)
                storage_limit = default_storage_limit(self.content, constants)

                # Assert
                self.assertEqual(expected_gas_limit, gas_limit)
                self.assertEqual(expected_storage_limit, storage_limit)
