from typing import Any
from typing import Dict

from pytezos.michelson.forge import forge_address
from pytezos.michelson.forge import forge_array
from pytezos.michelson.forge import forge_base58
from pytezos.michelson.forge import forge_bool
from pytezos.michelson.forge import forge_int
from pytezos.michelson.forge import forge_int16
from pytezos.michelson.forge import forge_int32
from pytezos.michelson.forge import forge_micheline
from pytezos.michelson.forge import forge_nat
from pytezos.michelson.forge import forge_public_key
from pytezos.michelson.forge import forge_script
from pytezos.rpc.kind import operation_tags

reserved_entrypoints = {
    'default': b'\x00',
    'root': b'\x01',
    'do': b'\x02',
    'set_delegate': b'\x03',
    'remove_delegate': b'\x04',
    'deposit': b'\x05',
}


def has_parameters(content: Dict[str, Any]) -> bool:
    if not content.get('parameters'):
        return False
    return not (content['parameters']['entrypoint'] == 'default' and content['parameters']['value'] == {'prim': 'Unit'})


def forge_entrypoint(entrypoint) -> bytes:
    """Encode Michelson contract entrypoint into the byte form.

    :param entrypoint: string
    """
    if entrypoint in reserved_entrypoints:
        return reserved_entrypoints[entrypoint]
    else:
        return b'\xff' + forge_array(entrypoint.encode(), len_bytes=1)


def forge_tag(operation_tag: int) -> bytes:
    return operation_tag.to_bytes(1, 'big')


def forge_operation(content: Dict[str, Any]) -> bytes:
    """Forge operation content (locally).

    :param content: {.., "kind": "transaction", ...}
    """
    encode_content = {
        'failing_noop': forge_failing_noop,
        'activate_account': forge_activate_account,
        'reveal': forge_reveal,
        'transaction': forge_transaction,
        'origination': forge_origination,
        'delegation': forge_delegation,
        'endorsement': forge_endorsement,
        'endorsement_with_slot': forge_endorsement_with_slot,
        'preattestation': forge_consensus_operation,
        'attestation': forge_consensus_operation,
        'attestation_with_dal': forge_consensus_operation,
        'preattestations_aggregate': forge_preattestations_aggregate,
        'attestations_aggregate': forge_attestations_aggregate,
        'double_consensus_operation_evidence': forge_double_consensus_operation_evidence,
        'register_global_constant': forge_register_global_constant,
        'transfer_ticket': forge_transfer_ticket,
        'smart_rollup_add_messages': forge_smart_rollup_add_messages,
        'smart_rollup_execute_outbox_message': forge_smart_rollup_execute_outbox_message,
    }
    encode_proc = encode_content.get(content['kind'])
    if not encode_proc:
        raise NotImplementedError(content['kind'])

    return encode_proc(content)


def forge_operation_group(operation_group: Dict[str, Any]) -> bytes:
    """Forge operation group (locally).

    :param operation_group: {"branch": "B...", "contents": [], ...}
    """
    res = forge_base58(operation_group['branch'])
    res += b''.join(map(forge_operation, operation_group['contents']))
    return res


def forge_activate_account(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_base58(content['pkh'])
    res += bytes.fromhex(content['secret'])
    return res


def forge_reveal(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_public_key(content['public_key'])

    if 'proof' in content:
        res += forge_bool(True)
        res += forge_array(forge_base58(content['proof']))
    else:
        res += forge_bool(False)

    return res


def forge_transaction(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_nat(int(content['amount']))
    res += forge_address(content['destination'])

    if has_parameters(content):
        res += forge_bool(True)
        res += forge_entrypoint(content['parameters']['entrypoint'])
        res += forge_array(forge_micheline(content['parameters']['value']))
    else:
        res += forge_bool(False)

    return res


def forge_origination(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_nat(int(content['balance']))

    if content.get('delegate'):
        res += forge_bool(True)
        res += forge_address(content['delegate'], tz_only=True)
    else:
        res += forge_bool(False)

    res += forge_script(content['script'])

    return res


def forge_delegation(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))

    if content.get('delegate'):
        res += forge_bool(True)
        res += forge_address(content['delegate'], tz_only=True)
    else:
        res += forge_bool(False)

    return res


def forge_endorsement(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_int32(int(content['level']))
    return res


def forge_inline_endorsement(content: Dict[str, Any]) -> bytes:
    res = forge_base58(content['branch'])
    res += forge_nat(operation_tags[content['operations']['kind']])
    res += forge_int32(int(content['operations']['level']))
    res += forge_base58(content['signature'])
    return res


def forge_endorsement_with_slot(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_array(forge_inline_endorsement(content['endorsement']))
    res += forge_int16(content['slot'])
    return res


def forge_consensus_content(content: Dict[str, Any]) -> bytes:
    """Forge the body shared by (pre)attestation ops: slot, level, round, block_payload_hash.

    Appends the DAL bitset (signed Zarith, Data_encoding.z) when `dal_attestation` is present.
    """
    res = forge_int16(int(content['slot']))
    res += forge_int32(int(content['level']))
    res += forge_int32(int(content['round']))
    res += forge_base58(content['block_payload_hash'])
    if content.get('dal_attestation') is not None:
        res += forge_int(int(content['dal_attestation']))
    return res


def _consensus_tag(content: Dict[str, Any]) -> int:
    """Resolve the consensus operation tag, switching `attestation` to the DAL tag when needed."""
    if content['kind'] == 'attestation' and content.get('dal_attestation') is not None:
        return operation_tags['attestation_with_dal']
    return operation_tags[content['kind']]


def forge_consensus_operation(content: Dict[str, Any]) -> bytes:
    """Forge a modern consensus operation: `attestation`, `preattestation` or `attestation_with_dal`."""
    res = forge_tag(_consensus_tag(content))
    res += forge_consensus_content(content)
    return res


def forge_inlined_consensus_operation(content: Dict[str, Any]) -> bytes:
    """Forge an inlined consensus operation (used inside denunciations).

    Layout: branch ‖ op-tag ‖ consensus_content ‖ [signature].
    """
    op = content['operations']
    res = forge_base58(content['branch'])
    res += forge_tag(_consensus_tag(op))
    res += forge_consensus_content(op)
    if content.get('signature'):
        res += forge_base58(content['signature'])
    return res


def forge_double_consensus_operation_evidence(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_int16(int(content['slot']))
    res += forge_array(forge_inlined_consensus_operation(content['op1']))
    res += forge_array(forge_inlined_consensus_operation(content['op2']))
    return res


def forge_consensus_aggregate_content(content: Dict[str, Any]) -> bytes:
    """Forge the aggregate consensus content: level, round, block_payload_hash (no slot)."""
    res = forge_int32(int(content['level']))
    res += forge_int32(int(content['round']))
    res += forge_base58(content['block_payload_hash'])
    return res


def forge_preattestations_aggregate(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_consensus_aggregate_content(content['consensus_content'])
    res += forge_array(b''.join(forge_int16(int(slot)) for slot in content['committee']))
    return res


def forge_attestations_aggregate(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_consensus_aggregate_content(content['consensus_content'])

    committee = b''
    for member in content['committee']:
        committee += forge_int16(int(member['slot']))
        if member.get('dal_attestation') is not None:
            committee += forge_bool(True)
            committee += forge_int(int(member['dal_attestation']))
        else:
            committee += forge_bool(False)
    res += forge_array(committee)
    return res


def forge_failing_noop(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_array(content['arbitrary'].encode())
    return res


def forge_register_global_constant(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_array(forge_micheline(content['value']))
    return res


def forge_transfer_ticket(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_array(forge_micheline(content['ticket_contents']))
    res += forge_array(forge_micheline(content['ticket_ty']))
    res += forge_address(content['ticket_ticketer'])
    res += forge_nat(int(content['ticket_amount']))
    res += forge_address(content['destination'])
    res += forge_array(content['entrypoint'].encode())
    return res


def forge_smart_rollup_add_messages(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_array(b''.join((forge_array(bytes.fromhex(msg)) for msg in content['message'])))
    return res


def forge_smart_rollup_execute_outbox_message(content: Dict[str, Any]) -> bytes:
    res = forge_tag(operation_tags[content['kind']])
    res += forge_address(content['source'], tz_only=True)
    res += forge_nat(int(content['fee']))
    res += forge_nat(int(content['counter']))
    res += forge_nat(int(content['gas_limit']))
    res += forge_nat(int(content['storage_limit']))
    res += forge_base58(content['rollup'])
    res += forge_base58(content['cemented_commitment'])
    res += forge_array(bytes.fromhex(content['output_proof']))
    return res
