from unittest import TestCase

from pytezos.crypto.encoding import base58_encode
from pytezos.operation.forge import forge_operation

# Raw 32/64-byte payloads encoded as the base58 strings pytezos consumes.
BPH_RAW = bytes(range(32))
BRANCH_RAW = bytes(range(32, 64))
SIG_RAW = bytes(range(64))

BPH = base58_encode(BPH_RAW, b'vh').decode()
BRANCH = base58_encode(BRANCH_RAW, b'B').decode()
SIG = base58_encode(SIG_RAW, b'sig').decode()


def _consensus_body(slot: int, level: int, round_: int) -> bytes:
    # slot(uint16) ‖ level(int32) ‖ round(int32) ‖ block_payload_hash(32)
    return slot.to_bytes(2, 'big') + level.to_bytes(4, 'big') + round_.to_bytes(4, 'big') + BPH_RAW


def _aggregate_body(level: int, round_: int) -> bytes:
    # level(int32) ‖ round(int32) ‖ block_payload_hash(32)  (no slot)
    return level.to_bytes(4, 'big') + round_.to_bytes(4, 'big') + BPH_RAW


class TestConsensusForging(TestCase):
    """Round-trip checks against the proto-025 byte layout (docs/notes/attestation-mental-model.md)."""

    def test_forge_attestation(self) -> None:
        content = {'kind': 'attestation', 'slot': 1, 'level': 2000000, 'round': 0, 'block_payload_hash': BPH}
        expected = b'\x15' + _consensus_body(1, 2000000, 0)
        self.assertEqual(expected, forge_operation(content))
        self.assertEqual(1 + 2 + 4 + 4 + 32, len(expected))

    def test_forge_preattestation(self) -> None:
        content = {'kind': 'preattestation', 'slot': 3, 'level': 42, 'round': 7, 'block_payload_hash': BPH}
        expected = b'\x14' + _consensus_body(3, 42, 7)
        self.assertEqual(expected, forge_operation(content))

    def test_forge_attestation_with_dal_field_switches_tag(self) -> None:
        # An `attestation` carrying a DAL bitset is forged under the attestation_with_dal tag (0x17).
        content = {
            'kind': 'attestation',
            'slot': 1,
            'level': 2000000,
            'round': 0,
            'block_payload_hash': BPH,
            'dal_attestation': 5,
        }
        # 5 -> Zarith natural -> single byte 0x05
        expected = b'\x17' + _consensus_body(1, 2000000, 0) + b'\x05'
        self.assertEqual(expected, forge_operation(content))

    def test_forge_attestation_with_dal_kind(self) -> None:
        content = {
            'kind': 'attestation_with_dal',
            'slot': 1,
            'level': 2000000,
            'round': 0,
            'block_payload_hash': BPH,
            'dal_attestation': 128,
        }
        # 128 -> signed Zarith (Data_encoding.z) -> 0x80 0x02
        expected = b'\x17' + _consensus_body(1, 2000000, 0) + b'\x80\x02'
        self.assertEqual(expected, forge_operation(content))

    def test_forge_dal_bitset_is_signed_zarith(self) -> None:
        # Boundary that catches the nat-vs-z bug: the DAL bitset uses signed Zarith
        # (Bitset.encoding = Data_encoding.z), so 64 -> 0x80 0x01, NOT the unsigned 0x40.
        content = {
            'kind': 'attestation_with_dal',
            'slot': 1,
            'level': 2000000,
            'round': 0,
            'block_payload_hash': BPH,
            'dal_attestation': 64,
        }
        forged = forge_operation(content)
        self.assertEqual(b'\x17' + _consensus_body(1, 2000000, 0) + b'\x80\x01', forged)
        self.assertTrue(forged.endswith(b'\x80\x01'))
        self.assertFalse(forged.endswith(b'\x40'))

    def test_forge_double_consensus_operation_evidence(self) -> None:
        inlined = {
            'branch': BRANCH,
            'operations': {'kind': 'attestation', 'slot': 1, 'level': 100, 'round': 0, 'block_payload_hash': BPH},
            'signature': SIG,
        }
        content = {'kind': 'double_consensus_operation_evidence', 'slot': 1, 'op1': inlined, 'op2': inlined}

        inlined_bytes = BRANCH_RAW + b'\x15' + _consensus_body(1, 100, 0) + SIG_RAW
        len_prefixed = len(inlined_bytes).to_bytes(4, 'big') + inlined_bytes
        expected = b'\x02' + (1).to_bytes(2, 'big') + len_prefixed + len_prefixed
        self.assertEqual(expected, forge_operation(content))

    def test_forge_inlined_consensus_without_signature(self) -> None:
        inlined = {
            'branch': BRANCH,
            'operations': {'kind': 'preattestation', 'slot': 2, 'level': 9, 'round': 1, 'block_payload_hash': BPH},
        }
        content = {'kind': 'double_consensus_operation_evidence', 'slot': 2, 'op1': inlined, 'op2': inlined}

        inlined_bytes = BRANCH_RAW + b'\x14' + _consensus_body(2, 9, 1)  # no signature trailer
        len_prefixed = len(inlined_bytes).to_bytes(4, 'big') + inlined_bytes
        expected = b'\x02' + (2).to_bytes(2, 'big') + len_prefixed + len_prefixed
        self.assertEqual(expected, forge_operation(content))

    def test_forge_preattestations_aggregate(self) -> None:
        content = {
            'kind': 'preattestations_aggregate',
            'consensus_content': {'level': 100, 'round': 0, 'block_payload_hash': BPH},
            'committee': [1, 2, 300],
        }
        committee = (1).to_bytes(2, 'big') + (2).to_bytes(2, 'big') + (300).to_bytes(2, 'big')
        expected = b'\x1e' + _aggregate_body(100, 0) + len(committee).to_bytes(4, 'big') + committee
        self.assertEqual(expected, forge_operation(content))

    def test_forge_attestations_aggregate(self) -> None:
        content = {
            'kind': 'attestations_aggregate',
            'consensus_content': {'level': 100, 'round': 0, 'block_payload_hash': BPH},
            'committee': [
                {'slot': 1},
                {'slot': 2, 'dal_attestation': 7},
            ],
        }
        committee = (1).to_bytes(2, 'big') + b'\x00'  # no dal
        committee += (2).to_bytes(2, 'big') + b'\xff' + b'\x07'  # dal present, bitset 7
        expected = b'\x1f' + _aggregate_body(100, 0) + len(committee).to_bytes(4, 'big') + committee
        self.assertEqual(expected, forge_operation(content))

    def test_legacy_endorsement_still_forges(self) -> None:
        # Back-compat: legacy endorsement (pre-Oxford) must keep working.
        self.assertEqual(b'\x00' + (5).to_bytes(4, 'big'), forge_operation({'kind': 'endorsement', 'level': 5}))


class TestConsensusContentBuilders(TestCase):
    def test_attestation_builder(self) -> None:
        from pytezos.operation.content import ContentMixin

        content = ContentMixin().attestation(slot=1, level=2, round=3, block_payload_hash=BPH)
        self.assertEqual(
            {'kind': 'attestation', 'slot': 1, 'level': 2, 'round': 3, 'block_payload_hash': BPH},
            content,
        )

    def test_attestation_builder_with_dal(self) -> None:
        from pytezos.operation.content import ContentMixin

        content = ContentMixin().attestation(slot=1, level=2, round=3, block_payload_hash=BPH, dal_attestation=9)
        self.assertEqual(9, content['dal_attestation'])

    def test_preattestation_builder(self) -> None:
        from pytezos.operation.content import ContentMixin

        content = ContentMixin().preattestation(slot=1, level=2, round=3, block_payload_hash=BPH)
        self.assertEqual('preattestation', content['kind'])

    def test_double_consensus_operation_evidence_builder(self) -> None:
        from pytezos.operation.content import ContentMixin

        op = {'branch': BRANCH, 'operations': {'kind': 'attestation'}}
        content = ContentMixin().double_consensus_operation_evidence(slot=4, op1=op, op2=op)
        self.assertEqual('double_consensus_operation_evidence', content['kind'])
        self.assertEqual(4, content['slot'])
