"""
Tests for the Semantic Analyzer (Milestone 3)
Run with: python -m pytest tests/test_semantic.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.lexer    import tokenize
from compiler.parser   import parse
from compiler.semantic import analyze


def run(src):
    ast = parse(tokenize(src))
    errors, sym_table = analyze(ast)
    return errors, sym_table


# ─── Valid programs ───────────────────────────────────────────────────────────
def test_valid_int_program():
    errors, _ = run("int x;\nx = 5 + 2;")
    assert errors == []

def test_valid_string_program():
    errors, _ = run('string s;\ns = "hello";')
    assert errors == []

def test_valid_if_else():
    src = "int a;\nint b;\na = 10;\nb = 5;\nif a > b then { a = 1; } else { b = 1; }"
    errors, _ = run(src)
    assert errors == []

def test_valid_while_loop():
    src = "int x;\nx = 5;\nwhile x > 0 do { x = x - 1; }"
    errors, _ = run(src)
    assert errors == []

def test_valid_while_with_extended_op():
    src = "int x;\nx = 10;\nwhile x >= 1 do { x = x - 1; }"
    errors, _ = run(src)
    assert errors == []

def test_valid_string_concat():
    errors, _ = run('string a;\nstring b;\nstring c;\na = "hello";\nb = " world";\nc = a + b;')
    assert errors == []

def test_valid_complex_expr():
    errors, _ = run("int x;\nint y;\nx = (3 + 4) * 2;\ny = x - 1;")
    assert errors == []


# ─── Type mismatches ─────────────────────────────────────────────────────────
def test_type_mismatch_string_to_int():
    errors, _ = run('int x;\nx = "hello";')
    assert any("Type mismatch" in e for e in errors)

def test_type_mismatch_int_to_string():
    errors, _ = run('string s;\ns = 42;')
    assert any("Type mismatch" in e for e in errors)

def test_mixed_types_in_expression():
    errors, _ = run("int x;\nstring s;\nx = 5;\ns = \"hi\";\nx = x + s;")
    assert any("mismatch" in e.lower() for e in errors)

def test_string_subtraction_invalid():
    errors, _ = run('string a;\nstring b;\na = "hi";\nb = "lo";\na = a - b;')
    assert any("not valid" in e or "mismatch" in e.lower() for e in errors)

def test_string_multiply_invalid():
    errors, _ = run('string a;\na = "hi";\na = a * a;')
    assert any("not valid" in e or "mismatch" in e.lower() for e in errors)


# ─── Undeclared / duplicate variables ────────────────────────────────────────
def test_undeclared_variable():
    errors, _ = run("int x;\nx = y + 1;")
    assert any("Undeclared" in e for e in errors)

def test_duplicate_declaration():
    errors, _ = run("int x;\nint x;")
    assert any("already declared" in e for e in errors)

def test_use_before_declaration():
    errors, _ = run("x = 5;\nint x;")
    assert any("Undeclared" in e for e in errors)


# ─── Scope isolation ─────────────────────────────────────────────────────────
def test_scope_isolation_if_block():
    """Variable declared inside an if-block must not be visible outside."""
    src = "int x;\nx = 1;\nif x > 0 then { int inner; inner = 1; }\ninner = 2;"
    errors, _ = run(src)
    assert any("Undeclared" in e and "inner" in e for e in errors)

def test_scope_isolation_else_block():
    """Variable declared inside an else-block must not be visible outside."""
    src = ("int x;\nx = 0;\n"
           "if x > 5 then { x = 1; } else { int tmp; tmp = 99; }\n"
           "tmp = 0;")
    errors, _ = run(src)
    assert any("Undeclared" in e and "tmp" in e for e in errors)

def test_scope_isolation_while_block():
    """Variable declared inside a while-body must not be visible outside."""
    src = "int x;\nx = 3;\nwhile x > 0 do { int inner; inner = x; x = x - 1; }\ninner = 0;"
    errors, _ = run(src)
    assert any("Undeclared" in e and "inner" in e for e in errors)

def test_outer_var_visible_inside_block():
    """Outer variables must remain accessible inside blocks."""
    src = "int x;\nx = 10;\nif x > 5 then { x = x - 1; }"
    errors, _ = run(src)
    assert errors == []


# ─── Condition type checking ──────────────────────────────────────────────────
def test_condition_type_mismatch():
    src = 'int x;\nstring s;\nx = 5;\ns = "hi";\nif x > s then { x = 1; }'
    errors, _ = run(src)
    assert any("mismatch" in e.lower() for e in errors)

def test_condition_same_type_ok():
    src = "int x;\nint y;\nx = 5;\ny = 3;\nif x >= y then { x = 1; }"
    errors, _ = run(src)
    assert errors == []


# ─── Symbol table ─────────────────────────────────────────────────────────────
def test_symbol_table_populated():
    _, sym = run("int x;\nstring name;")
    vars_  = sym.all_variables()
    assert vars_['x']['type']    == 'int'
    assert vars_['name']['type'] == 'string'

def test_symbol_table_scope_levels():
    """Global variables should be at level 0."""
    _, sym = run("int x;\nstring s;")
    vars_  = sym.all_variables()
    assert vars_['x']['level'] == 0
    assert vars_['s']['level'] == 0
