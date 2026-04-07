"""
Milestone 2: Syntax Analyzer (Parser)
Takes token stream and builds an Abstract Syntax Tree (AST).

Grammar:
    <program>     ::= <stmt_list>
    <stmt_list>   ::= <stmt>*
    <stmt>        ::= <decl_stmt> | <assign_stmt> | <if_stmt>
    <decl_stmt>   ::= <type> IDENTIFIER ;
    <assign_stmt> ::= IDENTIFIER = <expr> ;
    <if_stmt>     ::= if <condition> then { <stmt_list> } (else { <stmt_list> })?
    <condition>   ::= <expr> <cmp_op> <expr>
    <cmp_op>      ::= > | < | =
    <expr>        ::= <term> ('+' <term> | '-' <term>)*
    <term>        ::= <factor> ('*' <factor> | '/' <factor>)*
    <factor>      ::= NUMBER | STRING_LIT | IDENTIFIER | '(' <expr> ')'
    <type>        ::= int | string
"""

from .ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, StringNode, IdentifierNode, IfNode, ConditionNode
)


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens  = tokens
        self.pos     = 0

    # ─── Helpers ──────────────────────────────────────────────────────────────
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
                f"Line {tok.line}: Expected type '{expected_type}' but got '{tok.type}' ('{tok.value}')"
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

    # ─── Entry Point ─────────────────────────────────────────────────────────
    def parse(self):
        stmts = self.parse_stmt_list()
        if self.current() is not None:
            tok = self.current()
            raise ParseError(f"Line {tok.line}: Unexpected token '{tok.value}'")
        return ProgramNode(stmts)

    # ─── Statement List ───────────────────────────────────────────────────────
    def parse_stmt_list(self, stop_at_brace=False):
        stmts = []
        while self.current() is not None:
            if stop_at_brace and self.current().value == '}':
                break
            stmts.append(self.parse_stmt())
        return stmts

    # ─── Statement ────────────────────────────────────────────────────────────
    def parse_stmt(self):
        tok = self.current()
        if tok is None:
            raise ParseError("Expected a statement but reached end of input.")

        # if statement
        if tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if_stmt()

        # declaration: int x; or string name;
        if self.is_type_keyword():
            return self.parse_decl_stmt()

        # assignment: x = expr;
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

    # ─── If Statement ─────────────────────────────────────────────────────────
    def parse_if_stmt(self):
        if_tok = self.consume('KEYWORD', 'if')
        condition = self.parse_condition()
        self.consume('KEYWORD', 'then')
        self.consume('DELIMITER', '{')
        then_body = self.parse_stmt_list(stop_at_brace=True)
        self.consume('DELIMITER', '}')

        else_body = None
        if self.current() and self.current().type == 'KEYWORD' and self.current().value == 'else':
            self.consume('KEYWORD', 'else')
            self.consume('DELIMITER', '{')
            else_body = self.parse_stmt_list(stop_at_brace=True)
            self.consume('DELIMITER', '}')

        return IfNode(condition, then_body, else_body, line=if_tok.line)

    # ─── Condition ───────────────────────────────────────────────────────────
    def parse_condition(self):
        left = self.parse_expr()
        op_tok = self.current()
        if op_tok is None or op_tok.type != 'OPERATOR' or op_tok.value not in ('>', '<', '='):
            raise ParseError(
                f"Line {op_tok.line if op_tok else '?'}: Expected comparison operator (>, <, =)"
            )
        self.consume('OPERATOR')
        right = self.parse_expr()
        return ConditionNode(left, op_tok.value, right, line=op_tok.line)

    # ─── Expression ──────────────────────────────────────────────────────────
    def parse_expr(self):
        node = self.parse_term()
        while self.current() and self.current().type == 'OPERATOR' and self.current().value in ('+', '-'):
            op_tok = self.consume('OPERATOR')
            right  = self.parse_term()
            node   = BinOpNode(node, op_tok.value, right, line=op_tok.line)
        return node

    # ─── Term ─────────────────────────────────────────────────────────────────
    def parse_term(self):
        node = self.parse_factor()
        while self.current() and self.current().type == 'OPERATOR' and self.current().value in ('*', '/'):
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
            return IdentifierNode(tok.name if hasattr(tok, 'name') else tok.value, line=tok.line)

        if tok.type == 'DELIMITER' and tok.value == '(':
            self.consume('DELIMITER', '(')
            node = self.parse_expr()
            self.consume('DELIMITER', ')')
            return node

        raise ParseError(f"Line {tok.line}: Unexpected token '{tok.value}' in expression")


# ─── Public Entry ─────────────────────────────────────────────────────────────
def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()
