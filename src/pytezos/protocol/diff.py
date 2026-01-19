import difflib
import re
from os.path import dirname
from os.path import join

import simplejson as json

# Based on https://gist.github.com/noporpoise/16e731849eb1231e86d78f9dfeca3abc
_no_eol = r'\ No newline at end of file'
_hdr_pat = re.compile(r'^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$')
proj_dir = dirname(dirname(dirname(__file__)))


def make_patch(a, b, filename, context_size=0):
    """
    Get unified string diff between two strings. Trims top two lines.
    Returns empty string if strings are identical.
    """
    diffs = difflib.unified_diff(
        a=a.splitlines(True),
        b=b.splitlines(True),
        fromfile=filename,
        tofile=filename,
        n=context_size,
    )
    diffs = map(lambda x: x if x[-1] == '\n' else x + '\n' + _no_eol + '\n', diffs)
    return ''.join(diffs)


def apply_patch(source, patch, revert=False):
    """
    Apply patch to string s to recover newer string.
    If revert is True, treat s as the newer string, recover older string.
    """
    source = source.splitlines(True)
    patch = patch.splitlines(True)
    target = ''

    i = sl = 0
    midx, sign = (1, '+') if not revert else (3, '-')

    while i < len(patch) and patch[i].startswith(("---", "+++")):
        i += 1  # skip filename header

    while i < len(patch):
        match = _hdr_pat.match(patch[i])
        if not match:
            raise ValueError(f'Regex mismatch on line {i}, `{patch[i]}`')

        l = int(match.group(midx)) - 1 + (match.group(midx + 1) == '0')
        if sl > l or l > len(source):
            raise ValueError(f'Bad line num {i}: `{patch[i]}`')

        target += ''.join(source[sl:l])
        sl = l
        i += 1

        while i < len(patch) and patch[i][0] != '@':
            if i + 1 < len(patch) and patch[i + 1][0] == '\\':
                line = patch[i][:-1]
                i += 2
            else:
                line = patch[i]
                i += 1

            if len(line) > 0:
                if line[0] == sign or line[0] == ' ':
                    target += line[1:]
                sl += line[0] != sign

    target += ''.join(source[sl:])
    return target


def read_template(filename):
    with open(join(proj_dir, 'assets', filename)) as f:
        return f.read()


def generate_unidiff_html(diffs: list, output_path=None):
    html = read_template('unidiff.html')
    html = html.replace('{{text}}', json.dumps('\n'.join(diffs)))
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html)
        return None
    return html


def generate_jsondiff_html(left: dict, right: dict, output_path=None):
    html = read_template('jsondiff.html')
    html = html.replace('{{left}}', json.dumps(left))
    html = html.replace('{{right}}', json.dumps(right))
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html)
        return None
    return html
