import io
import os
import tarfile
from binascii import hexlify
from collections import OrderedDict
from tempfile import TemporaryDirectory
from typing import List
from typing import Tuple

import netstruct  # type: ignore
import requests
import simplejson as json
from tqdm import tqdm  # type: ignore

from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.key import blake2b_32
from pytezos.jupyter import InlineDocstring
from pytezos.jupyter import get_class_docstring
from pytezos.protocol.diff import apply_patch
from pytezos.protocol.diff import generate_unidiff_html
from pytezos.protocol.diff import make_patch


def dir_to_files(path) -> List[Tuple[str, str]]:
    files = []

    with open(os.path.join(path, 'TEZOS_PROTOCOL')) as f:
        index = json.load(f)

    for module in index['modules']:
        for ext in ['mli', 'ml']:
            name = f'{module.lower()}.{ext}'

            filename = os.path.join(path, name)
            if not os.path.exists(filename):
                continue

            with open(filename, 'r') as file:
                text = file.read()
                files.append((name, text))

    return files


def tar_to_files(path=None, raw=None) -> List[Tuple[str, str]]:
    assert path or raw

    fileobj = io.BytesIO(raw) if raw else None
    with tarfile.open(name=path, fileobj=fileobj) as tar, TemporaryDirectory() as tmp_dir:
        tar.extractall(tmp_dir)
        files = dir_to_files(tmp_dir)

    return files


def url_to_files(url) -> List[Tuple[str, str]]:
    res = requests.get(url, stream=True, timeout=60)
    raw = b''

    for data in tqdm(res.iter_content()):
        raw += data

    return tar_to_files(raw=raw)


def files_to_proto(files: List[Tuple[str, str]]) -> dict:
    components = OrderedDict()  # type: ignore

    for filename, text in files:
        name, ext = filename.split('.')
        key = {'mli': 'interface', 'ml': 'implementation'}[ext]
        name = name.capitalize()
        data = hexlify(text.encode()).decode()

        if name in components:
            components[name][key] = data
        else:
            components[name] = {'name': name, key: data}

    proto = {
        'expected_env_version': 0,  # TODO: this is V1
        'components': list(components.values()),
    }
    return proto


def files_to_tar(files: List[Tuple[str, str]], output_path=None):
    fileobj = io.BytesIO() if output_path is None else None
    nameparts = os.path.basename(output_path).split('.')
    mode = 'w'
    if len(nameparts) == 3:
        mode = f'w:{nameparts[-1]}'

    with tarfile.open(name=output_path, fileobj=fileobj, mode=mode) as tar:  # type: ignore[call-overload]
        for filename, text in files:
            file = io.BytesIO(text.encode())
            ti = tarfile.TarInfo(filename)
            ti.size = len(file.getvalue())
            tar.addfile(ti, file)

    if fileobj:
        return fileobj.getvalue()
    return None


def proto_to_files(proto: dict) -> List[Tuple[str, str]]:
    files = []
    extensions = {'interface': 'mli', 'implementation': 'ml'}

    for component in proto.get('components', []):
        for key, ext in extensions.items():
            if key in component:
                filename = f'{component["name"].lower()}.{ext}'
                text = bytes.fromhex(component[key]).decode()
                files.append((filename, text))

    return files


def proto_to_bytes(proto: dict) -> bytes:
    res = b''

    for component in proto.get('components', []):
        res += netstruct.pack(b'I$', component['name'].encode())

        if component.get('interface'):
            res += b'\xff' + netstruct.pack(b'I$', bytes.fromhex(component['interface']))
        else:
            res += b'\x00'

        # we should also handle patch case
        res += netstruct.pack(b'I$', bytes.fromhex(component.get('implementation', '')))

    res = netstruct.pack(b'hI$', proto['expected_env_version'], res)
    return res


class Protocol(metaclass=InlineDocstring):
    def __init__(self, proto):
        self._proto = proto

    def __repr__(self):
        res = [
            super().__repr__(),
            '\nHelpers',
            get_class_docstring(self.__class__),
        ]
        return '\n'.join(res)

    def __iter__(self):
        return iter(proto_to_files(self._proto))

    @classmethod
    def from_uri(cls, uri):
        """Loads protocol implementation from various sources and converts it to the RPC-like format.

        :param uri: link/path to a tar archive or path to a folder with extracted contents
        :returns: Protocol instance
        """
        if uri.startswith('http'):
            files = url_to_files(uri)
        elif os.path.exists(os.path.expanduser(uri)):
            files = tar_to_files(uri)
        elif os.path.isdir(uri):
            files = dir_to_files(uri)
        else:
            raise ValueError(uri)

        return Protocol(files_to_proto(files))

    def index(self) -> dict:
        """Generates TEZOS_PROTOCOL file.

        :returns: dict with protocol hash and modules
        """
        data = {
            'hash': self.hash(),
            'modules': list(map(lambda x: x['name'], self._proto.get('components', []))),
        }
        return data

    def export_tar(self, output_path=None):
        """Creates a tarball and dumps to a file or returns bytes.

        :param output_path: Path to the tarball [optional]. You can add .bz2 or .gz extension to make it compressed
        :returns: bytes if path is None or nothing
        """
        files = proto_to_files(self._proto)
        files.append(('TEZOS_PROTOCOL', json.dumps(self.index())))
        return files_to_tar(files, output_path)

    def export_html(self, output_path=None):
        """Generates github-like side-by-side diff viewe, powered by diff2html.js

        :param output_path: will write to this file if specified
        :returns: html string if path is not specified
        """
        diffs = [text for filename, text in self if text]
        return generate_unidiff_html(diffs, output_path=output_path)

    def diff(self, proto, context_size=3):
        """Calculates file diff between two protocol versions.

        :param proto: an instance of Protocol
        :param context_size: number of context lines before and after the change
        :returns: patch in proto format
        """
        files = []
        yours = dict(iter(self))
        theirs = proto_to_files(proto())

        for filename, their_text in theirs:
            patch = make_patch(
                a=yours.get(filename, ''),
                b=their_text,
                filename=filename,
                context_size=context_size,
            )
            files.append((filename, patch))

        return Protocol(files_to_proto(files))

    def patch(self, patch):
        """Applies unified diff and returns full-fledged protocol.

        :param patch: an instance of Protocol containing diff of files
        :returns: Protocol instance
        """
        files = []
        yours = dict(iter(self))
        diff = proto_to_files(patch())

        for filename, diff_text in diff:
            text = yours.get(filename, '')
            if diff_text:
                text = apply_patch(text, diff_text)
            files.append((filename, text))

        return Protocol(files_to_proto(files))

    def hash(self):
        hash_digest = blake2b_32(proto_to_bytes(self._proto)).digest()
        return base58_encode(hash_digest, b'P').decode()
