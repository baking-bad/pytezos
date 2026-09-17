import math
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional

from pytezos.operation.forge import forge_operation

DEFAULT_CONSTANTS = {
    'hard_gas_limit_per_operation': 1040000,
    'hard_storage_limit_per_operation': 60000,
}
# NOTE: Last update in Rio: https://gitlab.com/tezos/tezos/-/merge_requests/15993/diffs
DEFAULT_TRANSACTION_GAS_LIMIT = 3_040
DEFAULT_TRANSACTION_STORAGE_LIMIT = 257
# Mainnet defaults of the node's mempool filter (`/chains/main/mempool/filter`); other networks may differ
MINIMAL_FEES = 100
MINIMAL_MUTEZ_PER_BYTE = 1
MINIMAL_MUTEZ_PER_GAS_UNIT = 0.1


@dataclass(frozen=True)
class FeeThresholds:
    """Minimal fee thresholds a node accepts operations with (its mempool filter).

    Defaults are the mainnet values; a node may run with different ones (Tezos X sequencers do),
    in which case read them from the node via :meth:`from_mempool_filter`.
    """

    minimal_fees: int = MINIMAL_FEES
    minimal_mutez_per_byte: int = MINIMAL_MUTEZ_PER_BYTE
    minimal_nanotez_per_gas_unit: int = int(MINIMAL_MUTEZ_PER_GAS_UNIT * 1000)

    @classmethod
    def from_mempool_filter(cls, mempool_filter: Dict[str, Any]) -> 'FeeThresholds':
        """Build thresholds from a `/chains/main/mempool/filter` response.

        Rates come as nanotez fractions `[numerator, denominator]`; the per-byte one is rounded up to whole mutez
        so the quote never falls below the node's minimum.
        """
        gas_num, gas_den = (int(x) for x in mempool_filter['minimal_nanotez_per_gas_unit'])
        byte_num, byte_den = (int(x) for x in mempool_filter['minimal_nanotez_per_byte'])
        return cls(
            minimal_fees=int(mempool_filter['minimal_fees']),
            minimal_mutez_per_byte=math.ceil(byte_num / byte_den / 1000),
            minimal_nanotez_per_gas_unit=math.ceil(gas_num / gas_den),
        )


def calculate_fee(
    content: Dict[str, Any],
    consumed_gas: int,
    extra_size: int,
    reserve=10,
    minimal_nanotez_per_gas_unit: Optional[int] = None,
    thresholds: Optional[FeeThresholds] = None,
) -> int:
    """Calculate minimal required operation fee.

    :param content: operation content {..., "kind": "transaction", ... }
    :param consumed_gas: amount of gas consumed during the simulation (dry-run)
    :param extra_size: size of the additional operation data (branch, etc)
    :param reserve: safe reserve, just in case
    :param minimal_nanotez_per_gas_unit: override the per-gas rate only (kept for backward compatibility)
    :param thresholds: node fee thresholds, default is mainnet values
    """
    if thresholds is None:
        thresholds = FeeThresholds()
    size = len(forge_operation(content)) + extra_size
    if minimal_nanotez_per_gas_unit is None:
        minimal_nanotez_per_gas_unit = thresholds.minimal_nanotez_per_gas_unit
    fee = (
        thresholds.minimal_fees
        + thresholds.minimal_mutez_per_byte * size
        + int(minimal_nanotez_per_gas_unit * consumed_gas / 1000)
    )
    return fee + reserve


def default_fee(
    content: Dict[str, Any],
    gas_limit: Optional[int] = None,
    minimal_nanotez_per_gas_unit: Optional[int] = None,
    thresholds: Optional[FeeThresholds] = None,
) -> int:
    """Take hard gas limit instead of precise amount (no simulation) and calculate fee.

    :param content: operation content {..., "kind": "transaction", ... }
    """
    return calculate_fee(
        content=content,
        consumed_gas=gas_limit if gas_limit is not None else default_gas_limit(content),
        extra_size=32 + 64 + 3 * 3,  # branch, signature, fee:gas_limit:storage_limit mutez values (+3 bytes)
        minimal_nanotez_per_gas_unit=minimal_nanotez_per_gas_unit,
        thresholds=thresholds,
    )


def default_gas_limit(
    content: Dict[str, Any],
    constants: Optional[Dict[str, Any]] = None,
) -> int:
    """Get default gas limit by operation kind.

    :param content: operation content {..., "kind": "transaction", ... }
    :param constants: constants block from context
    """
    if constants is None:
        constants = DEFAULT_CONSTANTS
    values: Dict[str, int] = {
        'reveal': {'tz1': 176, 'tz2': 162, 'tz3': 1101, 'tz4': 1681}[content['source'][:3]],
        'delegation': 1000,
        'origination': int(constants['hard_gas_limit_per_operation']),
        'transaction': (
            int(constants['hard_gas_limit_per_operation'])
            if content.get('destination', '').startswith('KT')
            else DEFAULT_TRANSACTION_GAS_LIMIT
        ),
        'register_global_constant': int(constants['hard_gas_limit_per_operation']),
        'transfer_ticket': int(constants['hard_gas_limit_per_operation']),
        'smart_rollup_add_messages': int(constants['hard_gas_limit_per_operation']),
        'smart_rollup_execute_outbox_message': int(constants['hard_gas_limit_per_operation']),
    }
    return values[content['kind']]


def default_storage_limit(
    content,
    constants: Optional[Dict[str, Any]] = None,
) -> int:
    """Get default storage limit by operation kind.

    :param content: operation content {..., "kind": "transaction", ... }
    :param constants: constants block from context
    """
    if constants is None:
        constants = DEFAULT_CONSTANTS
    values: Dict[str, int] = {
        'reveal': 0,
        'delegation': 0,
        'origination': int(constants['hard_storage_limit_per_operation']),
        'transaction': (
            int(constants['hard_storage_limit_per_operation'])
            if content.get('destination', '').startswith('KT')
            else DEFAULT_TRANSACTION_STORAGE_LIMIT
        ),
        'register_global_constant': int(constants['hard_storage_limit_per_operation']),
        'transfer_ticket': int(constants['hard_storage_limit_per_operation']),
        'smart_rollup_add_messages': int(constants['hard_storage_limit_per_operation']),
        'smart_rollup_execute_outbox_message': int(constants['hard_storage_limit_per_operation']),
    }
    return values[content['kind']]
