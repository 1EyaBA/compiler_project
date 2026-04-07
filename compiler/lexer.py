"""
Milestone 1: Lexical Analyzer (Lexer / Scanner)
Converts raw source code into a stream of tokens.
"""

import re

# ─── Token Types ────────────────────────────────────────────────────────────
KEYWORDS = {'if', 'then', 'else', 'int', 'string'}

TOKEN_PATTERNS = [
    ('KEYWORD',     r'\b(if|then|else|int|string)\b'),
    ('NUMBER',      r'\d+'),
    ('STRING_LIT',  r'"[^"]*"'),
    ('IDENTIFIER',  r'[a-zA-Z_]\w*'),
    ('OPERATOR',    r'[+\-*/=><]'),
    ('DELIMITER',   r'[;{}()]'),
    ('NEWLINE',     r'\n'),
    ('WHITESPACE',  r'[ \t\r]+'),
]

MASTER_PATTERN = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS)


# ─── Token Class ─────────────────────────────────────────────────────────────
class Token:
    def __init__(self, type_, value, line=1):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"

    def display(self):
        """Short display for UI."""
        type_labels = {
            'KEYWORD':    'KW',
            'IDENTIFIER': 'ID',
            'NUMBER':     'NUM',
            'STRING_LIT': 'STR',
        }
        label = type_labels.get(self.type, self.type)
        return f"{label}({self.value!r})"


# ─── Tokenizer ────────────────────────────────────────────────────────────────
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

    # Check for characters that didn't match anything
    matched_chars = sum(len(mo.group()) for mo in re.finditer(MASTER_PATTERN, source_code))
    if matched_chars < len(source_code):
        # Find first bad character
        pos = 0
        cur_line = 1
        for mo in re.finditer(MASTER_PATTERN, source_code):
            if mo.start() > pos:
                bad_char = source_code[pos]
                raise SyntaxError(
                    f"Unexpected character '{bad_char}' at line {cur_line}, position {pos}"
                )
            if source_code[pos:mo.start()].count('\n'):
                cur_line += source_code[pos:mo.start()].count('\n')
            pos = mo.end()

    return tokens
