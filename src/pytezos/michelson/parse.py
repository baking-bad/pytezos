# Inspired by https://github.com/jansorg/tezos-intellij/blob/master/grammar/michelson.bnf
import json
import re
from typing import List
from typing import Optional

from ply.lex import Lexer  # type: ignore
from ply.lex import LexToken
from ply.lex import lex
from ply.yacc import yacc  # type: ignore

from pytezos.michelson.macros import expand_macro
from pytezos.michelson.macros import expr as make_expr
from pytezos.michelson.tags import prim_tags


def doc(docstring):
    def decorate(func):
        func.__doc__ = docstring
        return func

    return decorate


class MichelsonParserError(ValueError):
    def __init__(self, token: LexToken, message=None):
        message = message or f'failed to parse expression {token}'
        super(MichelsonParserError, self).__init__(message)
        self.message = message
        self.line = token.lineno
        self.pos = token.lexpos

    def format_stdout(self) -> str:
        return f'{self.line}:{self.pos}: {self.message}'


class Sequence(list):
    pass


class SimpleMichelsonLexer(Lexer):
    tokens = ('INT', 'BYTE', 'STR', 'ANNOT', 'PRIM', 'LEFT_CURLY', 'RIGHT_CURLY', 'LEFT_PAREN', 'RIGHT_PAREN', 'SEMI')

    t_INT = r'-?[0-9]+'
    t_BYTE = r'0x[A-Fa-f0-9]*'
    t_STR = r'\"(\\.|[^\"])*\"'
    t_ANNOT = r'[:@%]+([_0-9a-zA-Z\.]*)?'  # r'[:@%]+([_a-zA-Z][_0-9a-zA-Z\.]*)?'
    t_PRIM = r'[A-Za-z][A-Za-z0-9_]+'
    t_LEFT_CURLY = r'\{'
    t_RIGHT_CURLY = r'\}'
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'
    t_SEMI = r';'

    t_ignore_MULTI_COMMENT = r'/\*[^*]*\*/'
    t_ignore_COMMENT = r'#[^\n]*'
    t_ignore = ' \t\r\n\f'

    def __init__(self):
        super(SimpleMichelsonLexer, self).__init__()
        self.lexer = lex(module=self, reflags=re.MULTILINE)

    def t_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t


class MichelsonParser:
    """Customizable Michelson parser"""

    tokens = SimpleMichelsonLexer.tokens

    @doc('''instr : expr 
                  | empty''')
    def p_instr(self, p):
        p[0] = p[1]

    @doc('instr : INT')
    def p_instr_int(self, p):
        p[0] = {'int': p[1]}

    @doc('instr : BYTE')
    def p_instr_byte(self, p):
        p[0] = {'bytes': p[1][2:]}  # strip 0x prefix

    @doc('instr : STR')
    def p_instr_str(self, p):
        p[0] = {'string': json.loads(p[1])}

    @doc('instr : instr SEMI instr')
    def p_instr_list(self, p):
        p[0] = []
        for i in [p[1], p[3]]:
            if type(i) is list:
                p[0].extend(i)
            elif i is not None:
                p[0].append(i)

    @doc('instr : LEFT_CURLY instr RIGHT_CURLY')
    def p_instr_subseq(self, p):
        p[0] = Sequence()
        if type(p[2]) is list:
            p[0].extend(p[2])
        elif p[2] is not None:
            p[0].append(p[2])

    @doc('expr : PRIM annots args')
    def p_expr(self, p):
        prim = p[1]
        if prim in prim_tags or prim in self.extra_primitives:
            expr = make_expr(
                prim=prim,
                annots=p[2] or [],
                args=p[3] or [],
            )
        else:
            try:
                expr = expand_macro(
                    prim=prim,
                    annots=p[2] or [],
                    args=p[3] or [],
                )
            except AssertionError as e:
                raise MichelsonParserError(p.slice[1], str(e)) from e
        p[0] = Sequence(expr) if isinstance(expr, list) else expr

    @doc('''annots : annot 
                   | empty''')
    def p_annots(self, p):
        if p[1] is not None:
            p[0] = [p[1]]

    @doc('annots : annots annot')
    def p_annots_list(self, p):
        p[0] = []
        if type(p[1]) == list:
            p[0].extend(p[1])
        if p[2] is not None:
            p[0].append(p[2])

    @doc('annot : ANNOT')
    def p_annot(self, p):
        p[0] = p[1]

    @doc('''args : arg 
                 | empty''')
    def p_args(self, p):
        p[0] = []
        if p[1] is not None:
            p[0].append(p[1])

    @doc('args : args arg')
    def p_args_list(self, p):
        p[0] = []
        if type(p[1]) == list:
            p[0].extend(p[1])
        if p[2] is not None:
            p[0].append(p[2])

    @doc('arg : PRIM')
    def p_arg_prim(self, p):
        p[0] = {'prim': p[1]}

    @doc('arg : INT')
    def p_arg_int(self, p):
        p[0] = {'int': p[1]}

    @doc('arg : BYTE')
    def p_arg_byte(self, p):
        p[0] = {'bytes': p[1][2:]}  # strip 0x prefix

    @doc('arg : STR')
    def p_arg_str(self, p):
        p[0] = {'string': json.loads(p[1])}

    @doc('arg : LEFT_CURLY instr RIGHT_CURLY')
    def p_arg_subseq(self, p):
        if type(p[2]) == list:
            p[0] = p[2]
        elif p[2] is not None:
            p[0] = [p[2]]
        else:
            p[0] = []

    @doc('arg : LEFT_PAREN expr RIGHT_PAREN')
    def p_arg_group(self, p):
        p[0] = p[2]

    @doc('empty :')
    def p_empty(self, p): ...

    def p_error(self, p):
        raise MichelsonParserError(p)

    def __init__(self, debug=False, write_tables=False, extra_primitives: Optional[List[str]] = None):
        """Initialize Michelson parser

        :param debug: Verbose output
        :param write_tables: Store PLY output
        :param extra_primitives: List of words to be ignored
        """
        self.lexer = SimpleMichelsonLexer()
        self.parser = yacc(
            module=self,
            debug=debug,
            write_tables=write_tables,
        )
        self.extra_primitives = extra_primitives or []

    def parse(self, code):
        """Parse Michelson source.

        :param code: Michelson source
        :returns: Micheline expression
        """
        if len(code) > 0 and code[0] == '(' and code[-1] == ')':
            code = code[1:-1]
        return self.parser.parse(code)


def michelson_to_micheline(data, parser=None):
    """Converts Michelson source text into a Micheline expression.

    :param data: Michelson string
    :param parser: custom Michelson parser (optional)
    :returns: Micheline expression
    """
    if parser is None:
        parser = MichelsonParser()
    return parser.parse(data)
