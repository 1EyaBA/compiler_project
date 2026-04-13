"""
Tests for the Lexer (Milestone 1)
Run with: python -m pytest tests/test_lexer.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from compiler.lexer import tokenize, Token, spec_format


def token_list(src):
    return [(t.type, t.value) for t in tokenize(src)]


# ─── Basic tokens ─────────────────────────────────────────────────────────────
def test_simple_assignment():
    result = token_list("x = 5;")
    assert result == [
        ('IDENTIFIER', 'x'), ('OPERATOR', '='),
        ('NUMBER', '5'), ('DELIMITER', ';')
    ]

def test_arithmetic():
    result = token_list("x = 5 + 2;")
    assert ('OPERATOR', '+') in result
    assert ('NUMBER',   '5') in result
    assert ('NUMBER',   '2') in result

def test_all_arithmetic_operators():
    result = token_list("x = a + b - c * d / e;")
    ops = [v for t, v in result if t == 'OPERATOR']
    assert '=' in ops
    assert '+' in ops
    assert '-' in ops
    assert '*' in ops
    assert '/' in ops

def test_keywords_if_then_else():
    result = token_list("if x > 10 then { x = x - 1; }")
    types = [t for t, _ in result]
    assert 'KEYWORD' in types

def test_while_do_keywords():
    result = token_list("while x > 0 do { x = x - 1; }")
    kws = [v for t, v in result if t == 'KEYWORD']
    assert 'while' in kws
    assert 'do'    in kws

def test_string_literal():
    result = token_list('name = "Alice";')
    assert ('STRING_LIT', '"Alice"') in result

def test_declaration_int():
    result = token_list("int x;")
    assert result[0] == ('KEYWORD',    'int')
    assert result[1] == ('IDENTIFIER', 'x')

def test_declaration_string():
    result = token_list("string s;")
    assert result[0] == ('KEYWORD', 'string')

def test_line_tracking():
    tokens = tokenize("int x;\nx = 5;")
    assert tokens[0].line == 1
    assert tokens[3].line == 2

def test_unexpected_char():
    with pytest.raises(SyntaxError):
        tokenize("x = 5 @ 2;")

def test_multiline():
    src = "int a;\nint b;\na = 1;\nb = 2;"
    tokens = tokenize(src)
    assert len(tokens) > 0


# ─── Extended comparison operators ───────────────────────────────────────────
def test_compare_op_gt():
    result = token_list("if x > 0 then { x = 1; }")
    assert ('OPERATOR', '>') in result

def test_compare_op_lt():
    result = token_list("if x < 0 then { x = 1; }")
    assert ('OPERATOR', '<') in result

def test_compare_op_eq():
    result = token_list("if x == 0 then { x = 1; }")
    assert ('OPERATOR', '==') in result

def test_compare_op_gte():
    result = token_list("if x >= 5 then { x = 1; }")
    assert ('OPERATOR', '>=') in result

def test_compare_op_lte():
    result = token_list("if x <= 5 then { x = 1; }")
    assert ('OPERATOR', '<=') in result

def test_compare_op_neq():
    result = token_list("if x != 5 then { x = 1; }")
    assert ('OPERATOR', '!=') in result

def test_multi_char_ops_not_split():
    """>=  must be one token, not two."""
    result = token_list("x >= 5;")
    ops = [v for t, v in result if t == 'OPERATOR']
    assert '>=' in ops
    assert '>'  not in ops   # should NOT split into > and =


# ─── spec_format display ─────────────────────────────────────────────────────
def test_spec_format_basic():
    tokens = tokenize("x = 5 + 2;")
    out = spec_format(tokens)
    assert out == "[ID('x'), '=', NUM(5), '+', NUM(2), ';']"

def test_spec_format_keywords():
    tokens = tokenize("if a = b then")
    out = spec_format(tokens)
    assert "KW('if')" in out
    assert "ID('a')"  in out
    assert "KW('then')" in out

def test_spec_format_string():
    tokens = tokenize('name = "Alice";')
    out = spec_format(tokens)
    assert 'STR' in out
