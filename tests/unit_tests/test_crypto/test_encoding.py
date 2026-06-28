import pytest
from parameterized import parameterized  # type: ignore

from pytezos.crypto.encoding import base58_decode
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.encoding import is_bh
from pytezos.crypto.encoding import is_l2_pkh
from pytezos.crypto.encoding import is_pkh
from pytezos.crypto.encoding import is_sig
from pytezos.crypto.encoding import scrub_input


class TestEncoding:
    @pytest.mark.parametrize(
        ('base58', 'prefix'),
        [
            ('NetXdQprcVkpaWU', 'Net'),
            ('BKjWN8ALguCJ3oAjzMjZCNcFfUf1p9BfVAwYiVHs1QW3yMB9RNb', 'B'),
            ('oop1fbAVi2ZwEt3vpu4uKpYGbbxumyMBSWwWf9qbByeM4JYAu92', 'o'),
            ('LLoabcny4pVg1k6x3AktnNhwe1KSVBZh5Di45JeZPhUCmCu5Xj6ND', 'LLo'),
            ('PtCJ7pwoxe8JasnHY8YonnLYjcVHmhiARPJvqcC6VfHT5s8k8sY', 'P'),
            ('CoUeRwFZbV7NaAYRTz6n4ZLUkwiWcm7oKYdKCGcsEYHgVxSQxa4h', 'Co'),
            ('tz1eKkWU5hGtfLUiqNpucHrXymm83z3DG9Sq', 'tz1'),
            ('tz28YZoayJjVz2bRgGeVjxE8NonMiJ3r2Wdu', 'tz2'),
            ('tz3agP9LGe2cXmKQyYn6T68BHKjjktDbbSWX', 'tz3'),
            ('tz4F76GBmuLgXvUjLb2gfeBeM6fBf6EsuD1T', 'tz4'),
            ('tz5T7uDWfmUDvYw2kr6wfbe2ATYhRvKfLoFE', 'tz5'),
            ('txr1YNMEtkj5Vkqsbdmt7xaxBTMRZjzS96UAi', 'txr1'),
            ('edpku976gpuAD2bXyx1XGraeKuCo1gUZ3LAJcHM12W1ecxZwoiu22R', 'edpk'),
            ('sppk7aMNM3xh14haqEyaxNjSt7hXanCDyoWtRcxF8wbtya859ak6yZT', 'sppk'),
            ('p2pk679D18uQNkdjpRxuBXL5CqcDKTKzsiXVtc9oCUT6xb82zQmgUks', 'p2pk'),
            ('edsk3nM41ygNfSxVU4w1uAW3G9EnTQEB5rjojeZedLTGmiGRcierVv', 'edsk'),
            ('spsk1zkqrmst1yg2c4xi3crWcZPqgdc9KtPtb9SAZWYHAdiQzdHy7j', 'spsk'),
            ('p2sk3PM77YMR99AvD3fSSxeLChMdiQ6kkEzqoPuSwQqhPsh29irGLC', 'p2sk'),
            ('edesk1zxaPJkhNGSzgZDDSphvPzSNrnbmqes8xzUrw1wdFxdRT7ePiQz8D2Q18fMjn6fC9ZRS2rUbg8d8snxxznE', 'edesk'),
            ('spesk21cruoqtYmxfq5fpkXiZZRLRw4vh7VFJauGCAgHxZf3q6Q5LTv9m9dnMxyVjna6RzWQL45q4ppGLh97xZpV', 'spesk'),
            ('p2esk1rqdHRPz4xQh8uP8JaWSVnGFTKxkh2utdjK5CPDTXAzzh5sXnnobLkGrXEZzGhCKFDSjv8Ggrjt7PnobRzs', 'p2esk'),
            (
                'edsigtzLBGCyadERX1QsYHKpwnxSxEYQeGLnJGsSkHEsyY8vB5GcNdnvzUZDdFevJK7YZQ2ujwVjvQZn62ahCEcy74AwtbA8HuN',
                'edsig',
            ),
            (
                'spsig1RriZtYADyRhyNoQMa6AiPuJJ7AUDcrxWZfgqexzgANqMv4nXs6qsXDoXcoChBgmCcn2t7Y3EkJaVRuAmNh2cDDxWTdmsz',
                'spsig',
            ),
            ('sigUdRdXYCXW14xqT8mFTMkX4wSmDMBmcW1Vuz1vanGWqYTmuBodueUHGPUsbxgn73AroNwpEBHwPdhXUswzmvCzquiqtcHC', 'sig'),
            ('sr1JZsZT5u27MUQXeTh1aHqZBo8NvyxRKnyv', 'sr1'),
            ('src13FVgJq88nGcd3xmjtPr4j3wq9VJGkGZ3LaVKZ3PUT8dKbByviq', 'src1'),
            ('srs1257rrkFCsjuDS5enYG37uSas1J25daCaMQ2y5gPwwtoy8FqvDP', 'srs1'),
            ('BLsk1ijYmTDL6hfUvrFCqgwbetg6FTpHLbzPDKLAfP9tB9Cej8dME5', 'BLsk'),
            ('BLpk1q8T9TqRSNTacJU1WvTVtj62LZ8WZtGzZ3tQoQANzoXHwAPtxpJCY79TfoNu2m9N6RbFfh7s', 'BLpk'),
            (
                'BLsigB2azuvvpWDifK3xCMGDXUcF17V1R7NGfKQsUVrzm7718uvbjtrXpS3KMq5CSJiAWAS9Rjj79Zak3TskGGwDGfHnm52rvdb9rpJxtyXK39FNadwGX4EGtqXVDge9eDRjSm8bVNxJE6',
                'BLsig',
            ),
            ('BLesk1a3e2vNGbbPV5rFRHZZCHvZEvvtGP5Puer4yRfRVLR8E1xVyk5owiUeudZcaa31mGDmvbr9LH6ZPTUdi66z', 'BLesk'),
        ],
    )
    def test_b58_decode_encode(self, base58: str, prefix: str):
        expected: bytes = base58.encode()
        decoded: bytes = base58_decode(expected)
        print(decoded.hex())
        re_encoded = base58_encode(decoded, prefix.encode())
        assert re_encoded == expected

    @pytest.mark.parametrize(
        ('prefix', 'payload_len'),
        [
            (b'mdpk', 1312),  # ML-DSA-44 public key
            (b'mdsk', 3872),  # ML-DSA-44 secret key
            (b'mdesk', 3896),  # ML-DSA-44 encrypted secret key
            (b'mdsig', 2420),  # ML-DSA-44 signature
        ],
    )
    def test_mldsa_prefix_round_trip(self, prefix: bytes, payload_len: int):
        payload = bytes(range(256)) * (payload_len // 256) + bytes(range(payload_len % 256))
        encoded = base58_encode(payload, prefix)
        assert encoded.startswith(prefix)
        assert base58_decode(encoded) == payload

    @pytest.mark.parametrize(
        ('input_data', 'expected'),
        [
            ('test', b'test'),
            (b'test', b'test'),
            ('0x74657374', b'test'),
            ('74657374', b'test'),
        ],
    )
    def test_scrub_input(self, input_data, expected):
        assert scrub_input(input_data) == expected

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            ('tz1eKkWU5hGtfLUiqNpucHrXymm83z3DG9Sq', True),
            ('tz28YZoayJjVz2bRgGeVjxE8NonMiJ3r2Wdu', True),
            ('tz3agP9LGe2cXmKQyYn6T68BHKjjktDbbSWX', True),
            ('tz4F76GBmuLgXvUjLb2gfeBeM6fBf6EsuD1T', True),
            ('tz5T7uDWfmUDvYw2kr6wfbe2ATYhRvKfLoFE', True),
            ('txr1YNMEtkj5Vkqsbdmt7xaxBTMRZjzS96UAi', False),
            ('KT1ExvG3EjTrvDcAU7EqLNb77agPa5u6KvnY', False),
            ('qwerty', False),
            ('tz1eKkWU5hGtfLUiq', False),
        ],
    )
    def test_is_pkh(self, value, expected):
        assert is_pkh(value) == expected

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            ('tz1eKkWU5hGtfLUiqNpucHrXymm83z3DG9Sq', False),
            ('tz28YZoayJjVz2bRgGeVjxE8NonMiJ3r2Wdu', False),
            ('tz3agP9LGe2cXmKQyYn6T68BHKjjktDbbSWX', False),
            ('txr1YNMEtkj5Vkqsbdmt7xaxBTMRZjzS96UAi', True),
            ('KT1ExvG3EjTrvDcAU7EqLNb77agPa5u6KvnY', False),
            ('qwerty', False),
            ('tz1eKkWU5hGtfLUiq', False),
        ],
    )
    def test_is_l2_pkh(self, value, expected):
        assert is_l2_pkh(value) == expected

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            (
                'edsigtzLBGCyadERX1QsYHKpwnxSxEYQeGLnJGsSkHEsyY8vB5GcNdnvzUZDdFevJK7YZQ2ujwVjvQZn62ahCEcy74AwtbA8HuN',
                True,
            ),
            (
                'spsig1RriZtYADyRhyNoQMa6AiPuJJ7AUDcrxWZfgqexzgANqMv4nXs6qsXDoXcoChBgmCcn2t7Y3EkJaVRuAmNh2cDDxWTdmsz',
                True,
            ),
            (
                'BLsigB2azuvvpWDifK3xCMGDXUcF17V1R7NGfKQsUVrzm7718uvbjtrXpS3KMq5CSJiAWAS9Rjj79Zak3TskGGwDGfHnm52rvdb9rpJxtyXK39FNadwGX4EGtqXVDge9eDRjSm8bVNxJE6',
                True,
            ),
            ('BLsigB2azuvvpWDifK3xCMGDXUcF17V1R7NGfKQsUVrzm7718uvbjtrXpS3KMq5CSJiAWAS9Rjj79Zak3TskGGwDGfHnm52r', False),
            ('sigUdRdXYCXW14xqT8mFTMkX4wSmDMBmcW1Vuz1vanGWqYTmuBodueUHGPUsbxgn73AroNwpEBHwPdhXUswzmvCzquiqtcHC', True),
            ('qwerty', False),
            ('sigUdRdXYCXW14xqT8mFTMkX4wSmDMBmcW1Vuz1vanGWqYT', False),
        ],
    )
    def test_is_sig(self, value, expected):
        assert is_sig(value) == expected

    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            ('BLrbVv8rUfkpDZZ6efByhgjyDgPUFeKAfTMq8mWPmjXb9c5m8LJ', True),
            ('qwerty', False),
        ],
    )
    def test_is_bh(self, value, expected):
        assert is_bh(value) == expected
