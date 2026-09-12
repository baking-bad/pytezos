from unittest import TestCase

from parameterized import parameterized  # type: ignore

from pytezos.block.forge import PerBlockVote
from pytezos.block.forge import forge_per_block_votes
from pytezos.block.forge import forge_protocol_data

# Ushuaia (025): shadownet POST /chains/main/blocks/head/helpers/forge/protocol_data
USHUAIA_PREFIX = '023c529bc03ee2a6900c01a2c1f447acb8010b2823a38cd1edc73ffdaf41609700000000187a915b19aa000000'


class TestForgeProtocolData(TestCase):
    @parameterized.expand(
        [
            # https://rpc.tzkt.io/ithacanet/chains/main/blocks/10001/header/protocol_data
            (
                'ithaca_escape_vote_false',
                {
                    'payload_hash': 'vh2UTuqLs3Tf1Tr9HV51QJjvFHskzLydH1pNn3BfHdRiy8E5sDMf',
                    'payload_round': 1,
                    'proof_of_work_nonce': '7985fafeccd00d00',
                    'liquidity_baking_escape_vote': False,
                },
                '6939439d683b0d8258522f6c0c37a495776ed804ac68a04cf69292aaa6cc98d5000000017985fafeccd00d000000',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/2300002/header/protocol_data{,/raw}
            (
                'ithaca_escape_vote_true',
                {
                    'payload_hash': 'vh1m7uGhhgf4ARZ5zDtvk5fQvYDFFqKs7w6s5Ep5mdXRXiPAxNTg',
                    'payload_round': 0,
                    'proof_of_work_nonce': '6e2037c9297d0400',
                    'liquidity_baking_escape_vote': True,
                },
                '0b584612e23c4fe32d754f15c2b4536803161e03805aa5799c750d1120850be9000000006e2037c9297d040000ff',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/2600000/header/protocol_data{,/raw}
            (
                'jakarta_off_seed_nonce',
                {
                    'payload_hash': 'vh1wWcmFY9zZvBvWgM73EosSZnhK7n8XmSNMUmbPJTX4yShacvab',
                    'payload_round': 0,
                    'proof_of_work_nonce': '080342bceec00400',
                    'seed_nonce_hash': 'nceUUGNYEBYcRKY7vgSxDinUdwWJDkU9WNRzEamoidr391ZsR5yJa',
                    'liquidity_baking_toggle_vote': 'off',
                },
                '22f0b8c5bd4aa7cc28d79fcec52fa3944815626ee77faf4b320b302e8a7761be00000000080342bceec00400'
                'ff2081c6d2c04850701c2352aef3e9102ee70cadc961d0d56edf4c41bffe1bac4701',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/4500000/header/protocol_data{,/raw}
            (
                'nairobi_pass',
                {
                    'payload_hash': 'vh2mZe6Y4N7dcjLxrtxtYtM3igWdnj1rRLKdJX5GsPXxR1YctbL9',
                    'payload_round': 0,
                    'proof_of_work_nonce': '7821dc3197580100',
                    'liquidity_baking_toggle_vote': 'pass',
                },
                '900c6ce7fd70c797d771801c1a8ca0bc464d5f4087fef1b6e11afc2acb0c01ba000000007821dc31975801000002',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/5300000/header/protocol_data{,/raw}
            (
                'oxford_lb_on_ai_pass',
                {
                    'payload_hash': 'vh2XUSg7yjX4sdrYbb3wZQ21DdJ2svqA2cKzN73V7uadY2uaXKfU',
                    'payload_round': 0,
                    'proof_of_work_nonce': 'dd3a30f81d430200',
                    'liquidity_baking_toggle_vote': 'on',
                    'adaptive_issuance_vote': 'pass',
                },
                '700e6e6411c73f0978ccc28d69f21cfa0a1fbb1a2b11fd4104eb74b1de1d625c00000000dd3a30f81d4302000008',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/5760000/header/protocol_data{,/raw}
            (
                'paris_lb_on_ai_pass_seed_nonce',
                {
                    'payload_hash': 'vh1qmELijGpgo4kKyF7EdFC6zYS62UX7GPLnLqf83PHbMTAi58oj',
                    'payload_round': 0,
                    'proof_of_work_nonce': '0dcf32096b020000',
                    'seed_nonce_hash': 'nceVXvRToxWBEUDLyXi3fXXayZFgA6XmCvdLVa38FZXzmLXZhzymM',
                    'liquidity_baking_toggle_vote': 'on',
                    'adaptive_issuance_vote': 'pass',
                },
                '15e3808e17c6795280f841a181e445458b089c52a77202390723ea8b9a6da8c0000000000dcf32096b020000'
                'ffac81288ceff092f9ffbdcba0d6d30754dcd2dc08a71bc3e7a14a1ddad1a40cb208',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/5800002/header/protocol_data{,/raw}
            (
                'paris_lb_off_ai_pass',
                {
                    'payload_hash': 'vh2skKbepyFFDbPLuwRRT3A7CEeXkWrg9FZGVpTXGWdU4fgzxz4j',
                    'payload_round': 0,
                    'proof_of_work_nonce': '0dcf3209690d0100',
                    'liquidity_baking_toggle_vote': 'off',
                    'adaptive_issuance_vote': 'pass',
                },
                '9e1725c96a6f5eb7cf37cf3810be20716c1565b10425710c15321c580b0b08cb000000000dcf3209690d01000009',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/6000000/header/protocol_data{,/raw}
            (
                'paris_lb_pass_ai_pass_seed_nonce',
                {
                    'payload_hash': 'vh24qCihw7ctUHkCw6GRGSRcZPD99Cq8ovDu9ns2SBfTt2QGUnVH',
                    'payload_round': 0,
                    'proof_of_work_nonce': '1a991a03d9110100',
                    'seed_nonce_hash': 'nceUZ5yUXH8cD2ozh2W7pHCa7noynYD8FgQtCdkA4UfUS9ahjLaNv',
                    'liquidity_baking_toggle_vote': 'pass',
                    'adaptive_issuance_vote': 'pass',
                },
                '338ff101df63f91b52eb25a1f0c0273982babb372973020c94d4cd1582bce3b8000000001a991a03d9110100'
                'ff2b73f7a53a4f61629dc2e762fb6f2b821865392eed76fbb63bbb7708f5e9fa1f0a',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/6200000/header/protocol_data{,/raw}
            (
                'paris_lb_off_ai_off',
                {
                    'payload_hash': 'vh2JXYRVzJGWyLxgeuWWBeTF7AmZW1smTC3wdpLgbdMrsbFX959D',
                    'payload_round': 0,
                    'proof_of_work_nonce': 'bff0d300f0330000',
                    'liquidity_baking_toggle_vote': 'off',
                    'adaptive_issuance_vote': 'off',
                },
                '52a8dc0622b615ebe669c2bf08b5ea27de1db9f1b6703fa85c13afb28b12b13900000000bff0d300f03300000005',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/9000000/header/protocol_data{,/raw}
            (
                'rio_lb_on_ai_on',
                {
                    'payload_hash': 'vh2ZSYvh9ohaVxa1KSVDtiVSM6XchiuFabMyFdZs1y9CcBefSPTs',
                    'payload_round': 0,
                    'proof_of_work_nonce': '3f73c72483310100',
                    'liquidity_baking_toggle_vote': 'on',
                    'adaptive_issuance_vote': 'on',
                },
                '748606a22b5e6448de4c4e89f27628816571e3b606446b92ba085e56a683d5f7000000003f73c724833101000000',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/14000000/header/protocol_data{,/raw} (BLS-signed block)
            (
                'ushuaia_mainnet_on',
                {
                    'payload_hash': 'vh2icQCrVm7DH9yjQUSpzGNHPHXpNjgiaCky88Xbt3Qv8Hp5puu5',
                    'payload_round': 0,
                    'proof_of_work_nonce': '187a915b24d00200',
                    'liquidity_baking_toggle_vote': 'on',
                },
                '895840dadff55350824d08a19a7d720ac4629d6c6624f2a864ad6b61806791f700000000187a915b24d002000000',
            ),
            # https://rpc.tzkt.io/mainnet/chains/main/blocks/14906000/header/protocol_data{,/raw}
            (
                'ushuaia_mainnet_pass_seed_nonce',
                {
                    'payload_hash': 'vh3ahp6JbyxU2mqyrmoiQZxQ6CxsJLwnugaEuLwu1Dh9NmFtj4En',
                    'payload_round': 0,
                    'proof_of_work_nonce': '187a915baa140000',
                    'seed_nonce_hash': 'nceUyaKLVTeSod6AweWxedkYKeTa1Wpcv6AmUyTaDVUH4Q4C4KdEj',
                    'liquidity_baking_toggle_vote': 'pass',
                },
                'fb16750023259bdd62b1f1ba1159c69aa4e1e111e3ce6ff2c584bda7b8e31e6800000000187a915baa140000'
                'ff630eb874ffa734305db7dc3bcded2ffefee1b478e81275dfb0c88fdd6324095702',
            ),
            ('ushuaia_on', {'liquidity_baking_toggle_vote': 'on'}, USHUAIA_PREFIX + '00'),
            ('ushuaia_off', {'liquidity_baking_toggle_vote': 'off'}, USHUAIA_PREFIX + '01'),
            ('ushuaia_pass', {'liquidity_baking_toggle_vote': 'pass'}, USHUAIA_PREFIX + '02'),
            ('ushuaia_enum_member', {'liquidity_baking_toggle_vote': PerBlockVote.PASS}, USHUAIA_PREFIX + '02'),
        ]
    )
    def test_forge_protocol_data(self, _, protocol_data, expected) -> None:
        protocol_data = {
            'payload_hash': 'vh1h7Dit9ckbkM8znSGEpPdG8Xf6zrUhooKGHuAK84fGN41hgD67',
            'payload_round': 0,
            'proof_of_work_nonce': '187a915b19aa0000',
            **protocol_data,
        }
        self.assertEqual(expected, forge_protocol_data(protocol_data).hex())

    @parameterized.expand(
        [
            ('on', None, '00'),
            ('off', None, '01'),
            ('pass', None, '02'),
            ('on', 'on', '00'),
            ('on', 'off', '04'),
            ('on', 'pass', '08'),
            ('off', 'on', '01'),
            ('off', 'off', '05'),
            ('off', 'pass', '09'),
            ('pass', 'on', '02'),
            ('pass', 'off', '06'),
            ('pass', 'pass', '0a'),
        ]
    )
    def test_forge_per_block_votes(self, lb_vote, ai_vote, expected) -> None:
        protocol_data = {'liquidity_baking_toggle_vote': lb_vote}
        if ai_vote is not None:
            protocol_data['adaptive_issuance_vote'] = ai_vote
        self.assertEqual(expected, forge_per_block_votes(protocol_data).hex())

    @parameterized.expand(
        [
            ({'liquidity_baking_toggle_vote': 'yes'},),
            ({'liquidity_baking_toggle_vote': ''},),
            ({'liquidity_baking_toggle_vote': True},),
            ({'liquidity_baking_toggle_vote': 'on', 'adaptive_issuance_vote': 'maybe'},),
        ]
    )
    def test_invalid_vote_rejected(self, votes) -> None:
        protocol_data = {
            'payload_hash': 'vh1h7Dit9ckbkM8znSGEpPdG8Xf6zrUhooKGHuAK84fGN41hgD67',
            'payload_round': 0,
            'proof_of_work_nonce': '187a915b19aa0000',
            **votes,
        }
        with self.assertRaises(ValueError):
            forge_protocol_data(protocol_data)

    def test_vote_tags(self) -> None:
        self.assertEqual(0, PerBlockVote.ON.tag)
        self.assertEqual(1, PerBlockVote.OFF.tag)
        self.assertEqual(2, PerBlockVote.PASS.tag)
        self.assertIs(PerBlockVote.PASS, PerBlockVote('pass'))
        self.assertIs(PerBlockVote.OFF, PerBlockVote(PerBlockVote.OFF))
        self.assertEqual('off', f'{PerBlockVote.OFF}')
