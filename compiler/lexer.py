"""
Milestone 1: Lexical Analyzer (Lexer / Scanner)
Converts raw source code into a stream of tokens.

Token types:
  KEYWORD    — if, then, else, int, string, while, do
  IDENTIFIER — variable names like x, y, name
  NUMBER     — integer literals like 5, 10
  STRING_LIT — string literals like "hello"
  OPERATOR   — +, -, *, /, =, ==, >, <, >=, <=, !=
  DELIMITER  — ; { } ( )
"""

import re

# ─── Token Types ─────────────────────────────────────────────────────────────
KEYWORDS = {'if', 'then', 'else', 'int', 'string', 'while', 'do'}

# Order matters: multi-char operators MUST come before single-char ones
TOKEN_PATTERNS = [
    ('KEYWORD',     r'\b(if|then|else|int|string|while|do)\b'),
    ('NUMBER',      r'\d+'),
    ('STRING_LIT',  r'"[^"]*"'),
    ('IDENTIFIER',  r'[a-zA-Z_]\w*'),
    ('OPERATOR',    r'==|!=|>=|<=|[+\-*/=><]'),   # multi-char first
    ('DELIMITER',   r'[;{}()]'),
    ('NEWLINE',     r'\n'),
    ('WHITESPACE',  r'[ \t\r]+'),
]

MASTER_PATTERN = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS)

# Operators valid as comparison operators in conditions
COMPARE_OPS = {'>', '<', '=', '==', '>=', '<=', '!='}


# ─── Token Class ─────────────────────────────────────────────────────────────
class Token:
    def __init__(self, type_, value, line=1):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"

    def display(self):
        """Short display for UI chips."""
        type_labels = {
            'KEYWORD':    'KW',
            'IDENTIFIER': 'ID',
            'NUMBER':     'NUM',
            'STRING_LIT': 'STR',
        }
        label = type_labels.get(self.type, self.type)
        return f"{label}({self.value!r})"


# ─── Spec-format display ──────────────────────────────────────────────────────
def spec_format(tokens: list) -> str:
    """
    Returns a token stream string matching the project spec format.
    Example: [ID('x'), '=', NUM(5), '+', NUM(2), ';']
    """
    parts = []
    for t in tokens:
        if t.type == 'KEYWORD':
            parts.append(f"KW('{t.value}')")
        elif t.type == 'IDENTIFIER':
            parts.append(f"ID('{t.value}')")
        elif t.type == 'NUMBER':
            parts.append(f"NUM({t.value})")
        elif t.type == 'STRING_LIT':
            parts.append(f"STR({t.value})")
        else:
            parts.append(f"'{t.value}'")
    return '[' + ', '.join(parts) + ']'


# ─── Tokenizer ───────────────────────────────────────────────────────────────
def tokenize(source_code: str) -> list:
    """
    Converts source code string into a list of Token objects.
    Raises SyntaxError on unrecognized characters.
    """
    tokens = []
    line   = 1

    for mo in re.finditer(MASTER_PATTERN, source_code):
        kind  = mo.lastgroup
        value = mo.group()

        if kind == 'NEWLINE':
            line += 1
            continue
        elif kind == 'WHITESPACE':
            continue
        else:
            tokens.append(Token(kind, value, line))

    # Detect characters that matched nothing
    matched_end = 0
    cur_line    = 1
    for mo in re.finditer(MASTER_PATTERN, source_code):
        if mo.start() > matched_end:
            bad_char = source_code[matched_end]
            raise SyntaxError(
                f"Unexpected character '{bad_char}' at line {cur_line}, position {matched_end}"
            )
        cur_line    += source_code[matched_end:mo.start()].count('\n')
        matched_end  = mo.end()

    # Check trailing unmatched chars
    if matched_end < len(source_code):
        bad_char = source_code[matched_end]
        raise SyntaxError(
            f"Unexpected character '{bad_char}' at line {cur_line}, position {matched_end}"
        )

    return tokens
