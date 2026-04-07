"""
Tests for the Parser (Milestone 2)
Run with: python -m pytest tests/test_parser.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.lexer   import tokenize
from compiler.parser  import parse, ParseError
from compiler.ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, IdentifierNode, IfNode
)
import pytest


def compile_to_ast(src):
    return parse(tokenize(src))


def test_declaration():
    ast = compile_to_ast("int x;")
    assert isinstance(ast, ProgramNode)
    assert isinstance(ast.statements[0], DeclNode)
    assert ast.statements[0].var_type == 'int'
    assert ast.statements[0].name == 'x'


def test_assignment():
    ast = compile_to_ast("int x;\nx = 5;")
    assign = ast.statements[1]
    assert isinstance(assign, AssignNode)
    assert assign.name == 'x'
    assert isinstance(assign.expr, NumberNode)


def test_binary_op():
    ast = compile_to_ast("int x;\nx = 5 + 2;")
    expr = ast.statements[1].expr
    assert isinstance(expr, BinOpNode)
    assert expr.op == '+'


def test_if_statement():
    src = "int x;\nx = 10;\nif x > 5 then { x = x - 1; }"
    ast = compile_to_ast(src)
    if_node = ast.statements[2]
    assert isinstance(if_node, IfNode)
    assert if_node.else_body is None


def test_if_else():
    src = "int a;\na = 5;\nif a > 3 then { a = 1; } else { a = 0; }"
    ast = compile_to_ast(src)
    if_node = ast.statements[2]
    assert if_node.else_body is not None


def test_syntax_error_missing_semicolon():
    with pytest.raises(ParseError):
        compile_to_ast("int x\nx = 5;")


def test_syntax_error_bad_expression():
    with pytest.raises(ParseError):
        compile_to_ast("int x;\nx = ;")


def test_string_declaration():
    ast = compile_to_ast('string s;\ns = "hello";')
    decl = ast.statements[0]
    assert decl.var_type == 'string'
