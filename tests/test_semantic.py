"""
Tests for the Semantic Analyzer (Milestone 3)
Run with: python -m pytest tests/test_semantic.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.lexer     import tokenize
from compiler.parser    import parse
from compiler.semantic  import analyze


def run(src):
    ast = parse(tokenize(src))
    errors, sym_table = analyze(ast)
    return errors, sym_table


def test_valid_int_program():
    errors, _ = run("int x;\nx = 5 + 2;")
    assert errors == []


def test_valid_string_program():
    errors, _ = run('string s;\ns = "hello";')
    assert errors == []


def test_type_mismatch_string_to_int():
    errors, _ = run('int x;\nx = "hello";')
    assert any("Type mismatch" in e for e in errors)


def test_type_mismatch_int_to_string():
    errors, _ = run('string s;\ns = 42;')
    assert any("Type mismatch" in e for e in errors)


def test_undeclared_variable():
    errors, _ = run("int x;\nx = y + 1;")
    assert any("Undeclared" in e for e in errors)


def test_mixed_types_in_expression():
    errors, _ = run("int x;\nstring s;\nx = 5;\ns = \"hi\";\nx = x + s;")
    assert any("Type mismatch" in e or "mismatch" in e.lower() for e in errors)


def test_duplicate_declaration():
    errors, _ = run("int x;\nint x;")
    assert any("already declared" in e for e in errors)


def test_symbol_table_populated():
    _, sym = run("int x;\nstring name;")
    vars_ = sym.all_variables()
    assert vars_.get('x')    == 'int'
    assert vars_.get('name') == 'string'


def test_string_subtraction_invalid():
    errors, _ = run('string a;\nstring b;\na = "hi";\nb = "lo";\na = a - b;')
    assert any("not valid" in e or "mismatch" in e.lower() for e in errors)


def test_valid_if_else():
    src = "int a;\nint b;\na = 10;\nb = 5;\nif a > b then { a = 1; } else { b = 1; }"
    errors, _ = run(src)
    assert errors == []
