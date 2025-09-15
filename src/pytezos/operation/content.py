from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pytezos.jupyter import inline_doc


def format_mutez(value: Optional[Union[int, Decimal]]) -> str:
    """Format amount in mutez (10^-6).

    :param value: can be None (==0), Decimal (treated as tez), int (treated as mutez)
    :returns: amount in mutez, stringified
    """
    if value is None:
        value = 0
    elif isinstance(value, Decimal):
        value = int(value * 10**6)
    elif isinstance(value, float):
        raise ValueError('Please use decimal instead of float')
    return str(value)


def format_tez(value: Optional[Union[int, Decimal]]) -> Decimal:
    """Format amount in tez.

    :param value: can be None (==0), Decimal (treated as tez), int (treated as mutez)
    :rtype: Decimal
    """
    tez = Decimal(format_mutez(value)) / 10**6
    return tez.quantize(Decimal('0.000001'))


class ContentMixin:
    def operation(self, content: Dict[str, Any]):
        return content

    @inline_doc
    def endorsement(self, level: int) -> Dict[str, Any]:
        """Endorse a block.

        :param level: Endorsed level
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'endorsement',
                'level': level,
            }
        )

    @inline_doc
    def endorsement_with_slot(self, endorsement: dict, slot: int):
        """Wrap endorsement

        :param endorsement: Inlined endorsement
        :param slot: Minimum of the slots endorsed
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'endorsement_with_slot',
                'endorsement': endorsement,
                'slot': slot,
            }
        )

    @inline_doc
    def seed_nonce_revelation(self, level: int, nonce: str):
        """Reveal the nonce committed operation in the previous cycle.

        More info https://tezos.stackexchange.com/questions/567/what-are-nonce-revelations

        :param level: When nonce hash was committed
        :param nonce: Hex string
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'seed_nonce_revelation',
                'level': str(level),
                'nonce': nonce,
            }
        )

    @inline_doc
    def double_endorsement_evidence(self, op1: Dict[str, Any], op2: Dict[str, Any]):
        """Provide evidence of double endorsement (endorsing two different blocks at the same block height).

        Inline endorsement format:

        .. code-block:: python

            {
                "branch": $block_hash,
                "operations": {
                    "kind": "endorsement",
                    "level": integer ∈ [-2^31-2, 2^31+2]
                },
                "signature"?: $Signature
            }

        :param op1: Inline endorsement
        :param op2: Inline endorsement
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'double_endorsement_evidence',
                'op1': op1,
                'op2': op2,
            }
        )

    @inline_doc
    def double_baking_evidence(self, bh1: str, bh2: str):
        """Provide evidence of double baking (two different blocks at the same height).

        :param bh1: First block hash
        :param bh2: Second block hash
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'double_baking_evidence',
                'bh1': bh1,
                'bh2': bh2,
            }
        )

    @inline_doc
    def activate_account(self, activation_code='', pkh=''):
        """Activate recommended allocations for contributions to the TF fundraiser.

        More info https://activate.tezos.com/

        :param activation_code: Secret code from pdf, leave empty for autocomplete
        :param pkh: Public key hash, leave empty for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'activate_account',
                'pkh': pkh,
                'secret': activation_code,
            }
        )

    @inline_doc
    def proposals(self, proposals, source='', period=0):
        """Submit and/or upvote proposals to amend the protocol.

        Can only be submitted during a proposal period.
        More info https://tezos.gitlab.io/master/whitedoc/voting.html

        :param proposals: List of proposal hashes or single proposal hash
        :param source: Public key hash (of the signatory), leave None for autocomplete
        :param period: Number of the current voting period, leave 0 for autocomplete
        :returns: dict or OperationGroup
        """
        if not isinstance(proposals, list):
            proposals = [proposals]

        return self.operation(
            {
                'kind': 'proposals',
                'source': source,
                'period': str(period),
                'proposals': proposals,
            }
        )

    @inline_doc
    def ballot(self, proposal, ballot, source='', period=0):
        """Vote for a proposal in a given voting period.

        Can only be submitted during Testing_vote or Promotion_vote periods, and only once per period.
        More info https://tezos.gitlab.io/master/whitedoc/voting.html

        :param proposal: Hash of the proposal
        :param ballot: 'Yay', 'Nay' or 'Pass'
        :param source: Public key hash (of the signatory), leave None for autocomplete
        :param period: Number of the current voting period, leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'ballot',
                'source': source,
                'period': str(period),
                'proposal': proposal,
                'ballot': ballot,
            }
        )

    @inline_doc
    def reveal(
        self,
        public_key='',
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
        proof='',
    ):
        """Reveal the public key associated with a tz address.

        :param public_key: Public key to reveal, Base58 encoded
        :param source: Public key hash of the key revealed, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
            (More info https://tezos.stackexchange.com/questions/632/how-counter-grows)
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        contents = {
            'kind': 'reveal',
            'source': source,
            'fee': format_mutez(fee),
            'counter': str(counter),
            'gas_limit': str(gas_limit),
            'storage_limit': str(storage_limit),
            'public_key': public_key,
        }
        if proof:
            contents['proof'] = proof
        return self.operation(contents)

    @inline_doc
    def transaction(
        self,
        destination,
        amount=0,
        parameters=None,
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
    ):
        """Transfer tez to a given address (implicit or originated).

        If the receiver is a smart contract, then optional parameters may be passed.

        :param source: Address from which funds will be sent, leave None to use signatory address
        :param destination: Address
        :param amount: Amount to send in microtez (int) or tez (Decimal) (optional)
        :param counter: Current account counter, leave None for autocomplete
        :param parameters: { "entrypoint": $string, "value": $Micheline expression } (optional)
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        content = {
            'kind': 'transaction',
            'source': source,
            'fee': format_mutez(fee),
            'counter': str(counter),
            'gas_limit': str(gas_limit),
            'storage_limit': str(storage_limit),
            'amount': format_mutez(amount),
            'destination': destination,
        }

        if parameters is not None:
            content['parameters'] = parameters

        return self.operation(content)

    @inline_doc
    def origination(
        self,
        script,
        balance=0,
        delegate=None,
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
    ):
        """Deploy smart contract (scriptless KT accounts are not used for delegation since Babylon).

        :param script: {"code": $Micheline, "storage": $Micheline}
        :param balance: Amount transferred on the balance, WARNING: there is no default way to withdraw funds.
            More info: https://tezos.stackexchange.com/questions/1315/can-i-withdraw-funds-from-an-empty-smart-contract
        :param delegate: Set contract delegate, default None
        :param source: Address from which funds will be sent, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        content = {
            'kind': 'origination',
            'source': source,
            'fee': format_mutez(fee),
            'counter': str(counter),
            'gas_limit': str(gas_limit),
            'storage_limit': str(storage_limit),
            'balance': format_mutez(balance),
            'script': script,
        }

        if delegate is not None:
            content['delegate'] = delegate

        return self.operation(content)

    @inline_doc
    def delegation(
        self,
        delegate='',
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
    ):
        """Delegate funds or register yourself as a delegate.

        :param delegate: tz address of delegate, leave None to register yourself as a delegate
        :param source: Address from which funds will be delegated, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'delegation',
                'source': source,
                'fee': format_mutez(fee),
                'counter': str(counter),
                'gas_limit': str(gas_limit),
                'storage_limit': str(storage_limit),
                'delegate': delegate,
            }
        )

    @inline_doc
    def failing_noop(self, arbitrary: str):
        """Operation to sign arbitrary data without the risk it will be used onchain.

        :param arbitrary: Message to sign
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'failing_noop',
                'arbitrary': arbitrary,
            }
        )

    @inline_doc
    def register_global_constant(self, value: Any, source='', counter=0, fee=0, gas_limit=0, storage_limit=0):
        """Operation to register Micheline expressions in a global table of constants

        :param value: Micheline expression
        :param source: Address from which funds will be delegated, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'register_global_constant',
                'value': value,
                'source': source,
                'fee': format_mutez(fee),
                'counter': str(counter),
                'gas_limit': str(gas_limit),
                'storage_limit': str(storage_limit),
            }
        )

    @inline_doc
    def transfer_ticket(
        self,
        ticket_contents: Any,
        ticket_ty: Any,
        ticket_ticketer: str,
        ticket_amount: int,
        destination: str,
        entrypoint='default',
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
    ):
        """Transfer ticket to another implicit account or to a smart rollup

        :param ticket_contents: Micheline expression (value)
        :param ticket_ty: Micheline expression (type)
        :param ticket_ticketer: Ticketer address
        :param ticket_amount: Amount
        :param destination: Implicit or originated address (smart rollups not supported)
        :param entrypoint: Smart contract entrypoint (leave "default" for implicit accounts)
        :param source: Address from which funds will be delegated, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'transfer_ticket',
                'ticket_contents': ticket_contents,
                'ticket_ty': ticket_ty,
                'ticket_ticketer': ticket_ticketer,
                'ticket_amount': str(ticket_amount),
                'destination': destination,
                'entrypoint': entrypoint,
                'source': source,
                'fee': format_mutez(fee),
                'counter': str(counter),
                'gas_limit': str(gas_limit),
                'storage_limit': str(storage_limit),
            }
        )

    @inline_doc
    def smart_rollup_add_messages(
        self, message: List[bytes], source='', counter=0, fee=0, gas_limit=0, storage_limit=0
    ):
        """Send external message to the global rollup inbox

        :param message: Array of byte strings 2KB max each
        :param source: Address from which funds will be delegated, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'smart_rollup_add_messages',
                'message': [m.hex() for m in message],
                'source': source,
                'fee': format_mutez(fee),
                'counter': str(counter),
                'gas_limit': str(gas_limit),
                'storage_limit': str(storage_limit),
            }
        )

    @inline_doc
    def smart_rollup_execute_outbox_message(
        self,
        rollup: str,
        cemented_commitment: str,
        output_proof: bytes,
        source='',
        counter=0,
        fee=0,
        gas_limit=0,
        storage_limit=0,
    ):
        """Execute outbox message on L1

        :param rollup: Rollup address, base58 encoded (sr1)
        :param cemented_commitment: Commitment hash, base58 encoded (src1)
        :param output_proof: Byte string
        :param source: Address from which funds will be delegated, leave None to use signatory address
        :param counter: Current account counter, leave None for autocomplete
        :param fee: Leave None for autocomplete
        :param gas_limit: Leave None for autocomplete
        :param storage_limit: Leave None for autocomplete
        :returns: dict or OperationGroup
        """
        return self.operation(
            {
                'kind': 'smart_rollup_execute_outbox_message',
                'rollup': rollup,
                'cemented_commitment': cemented_commitment,
                'output_proof': output_proof.hex(),
                'source': source,
                'fee': format_mutez(fee),
                'counter': str(counter),
                'gas_limit': str(gas_limit),
                'storage_limit': str(storage_limit),
            }
        )
