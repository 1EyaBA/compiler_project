"""
Milestone 2: Syntax Analyzer (Parser)
Takes token stream and builds an Abstract Syntax Tree (AST).

─── Formal Grammar (BNF) ────────────────────────────────────────────────────

    <program>     ::= <stmt>*

    <stmt>        ::= <decl_stmt>
                    | <assign_stmt>
                    | <if_stmt>
                    | <while_stmt>

    <decl_stmt>   ::= <type> IDENTIFIER ;
    <type>        ::= int | string

    <assign_stmt> ::= IDENTIFIER = <expr> ;

    <if_stmt>     ::= if <condition> then { <stmt>* } ( else { <stmt>* } )?

    <while_stmt>  ::= while <condition> do { <stmt>* }

    <condition>   ::= <expr> <cmp_op> <expr>
    <cmp_op>      ::= > | < | = | == | >= | <= | !=

    <expr>        ::= <term> ( (+ | -) <term> )*

    <term>        ::= <factor> ( (* | /) <factor> )*

    <factor>      ::= NUMBER
                    | STRING_LIT
                    | IDENTIFIER
                    | ( <expr> )

─────────────────────────────────────────────────────────────────────────────

Note on = vs ==:
  Inside an `if` or `while` condition, a bare `=` is treated as equality
  comparison (per the language spec example: `if a = b then ...`).
  Outside a condition, `=` is always the assignment operator.
  Use `==` as an explicit equality operator — both are accepted.
"""

from .ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, StringNode, IdentifierNode,
    IfNode, WhileNode, ConditionNode
)
from .lexer import COMPARE_OPS


class ParseError(Exception):
    pass


# Tokens that mark a safe restart point after a syntax error (panic-mode sync)
_SYNC_VALUES = {';', '}', '{'}
_SYNC_KEYWORDS = {'if', 'while', 'int', 'string'}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # ─── Helpers ─────────────────────────────────────────────────────────────
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, expected_type=None, expected_value=None):
        tok = self.current()
        if tok is None:
            raise ParseError("Unexpected end of input.")
        if expected_type and tok.type != expected_type:
            raise ParseError(
                f"Line {tok.line}: Expected type '{expected_type}' "
                f"but got '{tok.type}' ('{tok.value}')"
            )
        if expected_value and tok.value != expected_value:
            raise ParseError(
                f"Line {tok.line}: Expected '{expected_value}' but got '{tok.value}'"
            )
        self.pos += 1
        return tok

    def is_type_keyword(self):
        tok = self.current()
        return tok and tok.type == 'KEYWORD' and tok.value in ('int', 'string')

    def is_compare_op(self):
        tok = self.current()
        return tok and tok.type == 'OPERATOR' and tok.value in COMPARE_OPS

    # ─── Entry Point ─────────────────────────────────────────────────────────────
    def parse(self):
        stmts, errors = self.parse_stmt_list()
        if self.current() is not None:
            tok = self.current()
            errors.append(f"Ligne {tok.line}: Token inattendu '{tok.value}'")
        return ProgramNode(stmts), errors

    # ─── Panic-mode synchronization ──────────────────────────────────────────────
    def _synchronize(self):
        """Skip tokens until we find a safe restart point."""
        while self.current() is not None:
            tok = self.current()
            # Stop BEFORE a keyword that starts a new statement
            if tok.type == 'KEYWORD' and tok.value in _SYNC_KEYWORDS:
                return
            # Stop AFTER a semicolon (consume it)
            if tok.type == 'DELIMITER' and tok.value == ';':
                self.pos += 1
                return
            # Stop AFTER a closing brace
            if tok.type == 'DELIMITER' and tok.value == '}':
                self.pos += 1
                return
            self.pos += 1

    # ─── Statement List ───────────────────────────────────────────────────────────
    def parse_stmt_list(self, stop_at_brace=False):
        stmts  = []
        errors = []
        while self.current() is not None:
            if stop_at_brace and self.current().value == '}':
                break
            try:
                stmts.append(self.parse_stmt())
            except ParseError as e:
                errors.append(str(e))
                self._synchronize()
        return stmts, errors

    # ─── Statement ───────────────────────────────────────────────────────────
    def parse_stmt(self):
        tok = self.current()
        if tok is None:
            raise ParseError("Expected a statement but reached end of input.")

        if tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if_stmt()

        if tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while_stmt()

        if self.is_type_keyword():
            return self.parse_decl_stmt()

        if tok.type == 'IDENTIFIER':
            return self.parse_assign_stmt()

        raise ParseError(f"Line {tok.line}: Unexpected token '{tok.value}'")

    # ─── Declaration ─────────────────────────────────────────────────────────
    def parse_decl_stmt(self):
        type_tok = self.consume('KEYWORD')
        name_tok = self.consume('IDENTIFIER')
        self.consume('DELIMITER', ';')
        return DeclNode(type_tok.value, name_tok.value, line=type_tok.line)

    # ─── Assignment ──────────────────────────────────────────────────────────
    def parse_assign_stmt(self):
        name_tok = self.consume('IDENTIFIER')
        self.consume('OPERATOR', '=')
        expr = self.parse_expr()
        self.consume('DELIMITER', ';')
        return AssignNode(name_tok.value, expr, line=name_tok.line)

    # ─── If Statement ───────────────────────────────────────────────────────────
    def parse_if_stmt(self):
        if_tok = self.consume('KEYWORD', 'if')
        condition = self.parse_condition()
        self.consume('KEYWORD', 'then')
        self.consume('DELIMITER', '{')
        then_body, then_errors = self.parse_stmt_list(stop_at_brace=True)
        if then_errors:
            raise ParseError(then_errors[0])
        self.consume('DELIMITER', '}')

        else_body = None
        if (self.current()
                and self.current().type == 'KEYWORD'
                and self.current().value == 'else'):
            self.consume('KEYWORD', 'else')
            self.consume('DELIMITER', '{')
            else_body, else_errors = self.parse_stmt_list(stop_at_brace=True)
            if else_errors:
                raise ParseError(else_errors[0])
            self.consume('DELIMITER', '}')

        return IfNode(condition, then_body, else_body, line=if_tok.line)

    # ─── While Statement ───────────────────────────────────────────────────────────
    def parse_while_stmt(self):
        while_tok = self.consume('KEYWORD', 'while')
        condition = self.parse_condition()
        self.consume('KEYWORD', 'do')
        self.consume('DELIMITER', '{')
        body, body_errors = self.parse_stmt_list(stop_at_brace=True)
        if body_errors:
            raise ParseError(body_errors[0])
        self.consume('DELIMITER', '}')
        return WhileNode(condition, body, line=while_tok.line)

    # ─── Condition ───────────────────────────────────────────────────────────
    def parse_condition(self):
        left = self.parse_expr()
        if not self.is_compare_op():
            tok = self.current()
            line = tok.line if tok else '?'
            val  = tok.value if tok else 'EOF'
            raise ParseError(
                f"Line {line}: Expected comparison operator "
                f"(>, <, =, ==, >=, <=, !=) but got '{val}'"
            )
        op_tok = self.consume('OPERATOR')
        right  = self.parse_expr()
        return ConditionNode(left, op_tok.value, right, line=op_tok.line)

    # ─── Expression ──────────────────────────────────────────────────────────
    def parse_expr(self):
        node = self.parse_term()
        while (self.current()
               and self.current().type == 'OPERATOR'
               and self.current().value in ('+', '-')):
            op_tok = self.consume('OPERATOR')
            right  = self.parse_term()
            node   = BinOpNode(node, op_tok.value, right, line=op_tok.line)
        return node

    # ─── Term ────────────────────────────────────────────────────────────────
    def parse_term(self):
        node = self.parse_factor()
        while (self.current()
               and self.current().type == 'OPERATOR'
               and self.current().value in ('*', '/')):
            op_tok = self.consume('OPERATOR')
            right  = self.parse_factor()
            node   = BinOpNode(node, op_tok.value, right, line=op_tok.line)
        return node

    # ─── Factor ──────────────────────────────────────────────────────────────
    def parse_factor(self):
        tok = self.current()
        if tok is None:
            raise ParseError("Unexpected end of input in expression.")

        if tok.type == 'NUMBER':
            self.consume('NUMBER')
            return NumberNode(tok.value, line=tok.line)

        if tok.type == 'STRING_LIT':
            self.consume('STRING_LIT')
            return StringNode(tok.value.strip('"'), line=tok.line)

        if tok.type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            return IdentifierNode(tok.value, line=tok.line)

        if tok.type == 'DELIMITER' and tok.value == '(':
            self.consume('DELIMITER', '(')
            node = self.parse_expr()
            self.consume('DELIMITER', ')')
            return node

        raise ParseError(f"Line {tok.line}: Unexpected token '{tok.value}' in expression")


# ─── Public Entry ─────────────────────────────────────────────────────────────────────
def parse(tokens):
    """Returns (ProgramNode, [error_strings]). Never raises."""
    parser = Parser(tokens)
    return parser.parse()
