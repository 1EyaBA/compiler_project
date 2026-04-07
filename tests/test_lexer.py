"""
Tests for the Lexer (Milestone 1)
Run with: python -m pytest tests/test_lexer.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.lexer import tokenize, Token

def token_list(src):
    return [(t.type, t.value) for t in tokenize(src)]

def test_simple_assignment():
    result = token_list("x = 5;")
    assert result == [('IDENTIFIER','x'), ('OPERATOR','='), ('NUMBER','5'), ('DELIMITER',';')]

def test_arithmetic():
    result = token_list("x = 5 + 2;")
    assert ('OPERATOR', '+') in result
    assert ('NUMBER', '5') in result
    assert ('NUMBER', '2') in result

def test_keywords():
    result = token_list("if x > 10 then { x = x - 1; }")
    types = [t for t, _ in result]
    assert 'KEYWORD' in types

def test_string_literal():
    result = token_list('name = "Alice";')
    assert ('STRING_LIT', '"Alice"') in result

def test_declaration():
    result = token_list("int x;")
    assert result[0] == ('KEYWORD', 'int')
    assert result[1] == ('IDENTIFIER', 'x')

def test_line_tracking():
    tokens = tokenize("int x;\nx = 5;")
    assert tokens[0].line == 1
    assert tokens[3].line == 2

def test_unexpected_char():
    import pytest
    with pytest.raises(SyntaxError):
        tokenize("x = 5 @ 2;")

def test_multiline():
    src = "int a;\nint b;\na = 1;\nb = 2;"
    tokens = tokenize(src)
    assert len(tokens) > 0
