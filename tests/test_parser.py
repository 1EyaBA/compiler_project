"""
Tests for the Parser (Milestone 2)
Run with: python -m pytest tests/test_parser.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from compiler.lexer    import tokenize
from compiler.parser   import parse, ParseError
from compiler.ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, StringNode, IdentifierNode,
    IfNode, WhileNode, ConditionNode
)


def ast(src):
    return parse(tokenize(src))


# ─── Declarations ─────────────────────────────────────────────────────────────
def test_int_declaration():
    tree = ast("int x;")
    assert isinstance(tree.statements[0], DeclNode)
    assert tree.statements[0].var_type == 'int'
    assert tree.statements[0].name     == 'x'

def test_string_declaration():
    tree = ast("string s;")
    decl = tree.statements[0]
    assert decl.var_type == 'string'


# ─── Assignments ──────────────────────────────────────────────────────────────
def test_assignment_number():
    tree   = ast("int x;\nx = 5;")
    assign = tree.statements[1]
    assert isinstance(assign, AssignNode)
    assert isinstance(assign.expr, NumberNode)
    assert assign.expr.value == 5

def test_assignment_string():
    tree   = ast('string s;\ns = "hello";')
    assign = tree.statements[1]
    assert isinstance(assign.expr, StringNode)
    assert assign.expr.value == 'hello'


# ─── Expressions ──────────────────────────────────────────────────────────────
def test_binary_add():
    tree = ast("int x;\nx = 5 + 2;")
    expr = tree.statements[1].expr
    assert isinstance(expr, BinOpNode)
    assert expr.op == '+'

def test_binary_multiply():
    tree = ast("int x;\nx = 3 * 4;")
    expr = tree.statements[1].expr
    assert isinstance(expr, BinOpNode)
    assert expr.op == '*'

def test_nested_expression_with_parens():
    tree = ast("int x;\nx = (3 + 4) * 2;")
    expr = tree.statements[1].expr
    assert isinstance(expr, BinOpNode)
    assert expr.op == '*'
    assert isinstance(expr.left, BinOpNode)   # (3+4) is the left child

def test_operator_precedence():
    """3 + 4 * 2 should parse as 3 + (4 * 2), not (3+4)*2."""
    tree = ast("int x;\nx = 3 + 4 * 2;")
    expr = tree.statements[1].expr
    assert expr.op == '+'
    assert isinstance(expr.right, BinOpNode)
    assert expr.right.op == '*'


# ─── If / Else ────────────────────────────────────────────────────────────────
def test_if_no_else():
    tree = ast("int x;\nx = 10;\nif x > 5 then { x = x - 1; }")
    if_node = tree.statements[2]
    assert isinstance(if_node, IfNode)
    assert if_node.else_body is None

def test_if_else():
    src  = "int a;\na = 5;\nif a > 3 then { a = 1; } else { a = 0; }"
    tree = ast(src)
    if_node = tree.statements[2]
    assert isinstance(if_node, IfNode)
    assert if_node.else_body is not None

def test_if_condition_stored():
    tree    = ast("int x;\nif x > 0 then { x = 1; }")
    if_node = tree.statements[1]
    assert isinstance(if_node.condition, ConditionNode)
    assert if_node.condition.op == '>'


# ─── While loop ───────────────────────────────────────────────────────────────
def test_while_basic():
    src  = "int x;\nx = 5;\nwhile x > 0 do { x = x - 1; }"
    tree = ast(src)
    while_node = tree.statements[2]
    assert isinstance(while_node, WhileNode)

def test_while_condition():
    src  = "int x;\nx = 10;\nwhile x >= 1 do { x = x - 1; }"
    tree = ast(src)
    wn   = tree.statements[2]
    assert isinstance(wn.condition, ConditionNode)
    assert wn.condition.op == '>='

def test_while_body_stmts():
    src  = "int x;\nint y;\nwhile x > 0 do { x = x - 1; y = y + 1; }"
    tree = ast(src)
    wn   = tree.statements[2]
    assert len(wn.body) == 2

def test_while_body_can_have_if():
    src = ("int x;\nint y;\nx = 10;\ny = 0;\n"
           "while x > 0 do {\n"
           "  x = x - 1;\n"
           "  if x > 5 then { y = y + 1; }\n"
           "}")
    tree = ast(src)
    wn   = tree.statements[4]
    assert isinstance(wn, WhileNode)
    assert any(isinstance(s, IfNode) for s in wn.body)


# ─── Extended comparison operators ───────────────────────────────────────────
def test_condition_eq_double():
    tree    = ast("int x;\nif x == 0 then { x = 1; }")
    if_node = tree.statements[1]
    assert if_node.condition.op == '=='

def test_condition_gte():
    tree    = ast("int x;\nif x >= 5 then { x = 1; }")
    if_node = tree.statements[1]
    assert if_node.condition.op == '>='

def test_condition_lte():
    tree    = ast("int x;\nif x <= 5 then { x = 1; }")
    if_node = tree.statements[1]
    assert if_node.condition.op == '<='

def test_condition_neq():
    tree    = ast("int x;\nif x != 0 then { x = 1; }")
    if_node = tree.statements[1]
    assert if_node.condition.op == '!='


# ─── Syntax errors ────────────────────────────────────────────────────────────
def test_syntax_error_missing_semicolon():
    with pytest.raises(ParseError):
        ast("int x\nx = 5;")

def test_syntax_error_bad_expression():
    with pytest.raises(ParseError):
        ast("int x;\nx = ;")

def test_syntax_error_missing_then():
    with pytest.raises(ParseError):
        ast("int x;\nif x > 0 { x = 1; }")

def test_syntax_error_missing_do():
    with pytest.raises(ParseError):
        ast("int x;\nwhile x > 0 { x = x - 1; }")

def test_syntax_error_unclosed_brace():
    with pytest.raises(ParseError):
        ast("int x;\nif x > 0 then { x = 1;")
