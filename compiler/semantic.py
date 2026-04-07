"""
Milestone 3: Semantic Analyzer
Walks the AST and checks for:
  - Undeclared variables
  - Duplicate declarations
  - Type mismatches in assignments
  - Type mismatches in binary operations
  - Type mismatches in conditions
"""

from .ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, StringNode, IdentifierNode, IfNode, ConditionNode
)
from .symbol_table import SymbolTable


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors       = []

    def analyze(self, ast: ProgramNode):
        self.visit_program(ast)
        return self.errors

    # ─── Visitors ─────────────────────────────────────────────────────────────
    def visit_program(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit_stmt(stmt)

    def visit_stmt(self, node):
        if isinstance(node, DeclNode):
            self.visit_decl(node)
        elif isinstance(node, AssignNode):
            self.visit_assign(node)
        elif isinstance(node, IfNode):
            self.visit_if(node)
        else:
            self.errors.append(f"Unknown statement type: {type(node).__name__}")

    def visit_decl(self, node: DeclNode):
        try:
            self.symbol_table.declare(node.name, node.var_type, line=node.line)
        except Exception as e:
            self.errors.append(str(e))

    def visit_assign(self, node: AssignNode):
        # Variable must be declared
        try:
            declared_type = self.symbol_table.lookup(node.name, line=node.line)
        except Exception as e:
            self.errors.append(str(e))
            return

        # Infer type of the expression
        expr_type = self.infer_type(node.expr)
        if expr_type is None:
            return  # error already recorded during inference

        if declared_type != expr_type:
            self.errors.append(
                f"Line {node.line}: Type mismatch — cannot assign '{expr_type}' "
                f"to variable '{node.name}' of type '{declared_type}'."
            )

    def visit_if(self, node: IfNode):
        self.visit_condition(node.condition)
        self.symbol_table.push_scope()
        for stmt in node.then_body:
            self.visit_stmt(stmt)
        self.symbol_table.pop_scope()

        if node.else_body:
            self.symbol_table.push_scope()
            for stmt in node.else_body:
                self.visit_stmt(stmt)
            self.symbol_table.pop_scope()

    def visit_condition(self, node: ConditionNode):
        left_type  = self.infer_type(node.left)
        right_type = self.infer_type(node.right)
        if left_type and right_type and left_type != right_type:
            self.errors.append(
                f"Line {node.line}: Type mismatch in condition — "
                f"cannot compare '{left_type}' with '{right_type}'."
            )

    # ─── Type Inference ──────────────────────────────────────────────────────
    def infer_type(self, node) -> str:
        if isinstance(node, NumberNode):
            return 'int'

        if isinstance(node, StringNode):
            return 'string'

        if isinstance(node, IdentifierNode):
            try:
                return self.symbol_table.lookup(node.name, line=node.line)
            except Exception as e:
                self.errors.append(str(e))
                return None

        if isinstance(node, BinOpNode):
            left_type  = self.infer_type(node.left)
            right_type = self.infer_type(node.right)

            if left_type is None or right_type is None:
                return None   # error already logged

            if left_type != right_type:
                self.errors.append(
                    f"Line {node.line}: Type mismatch in expression — "
                    f"cannot apply '{node.op}' to '{left_type}' and '{right_type}'."
                )
                return None

            # Only + is valid for strings; -, *, / are int-only
            if left_type == 'string' and node.op != '+':
                self.errors.append(
                    f"Line {node.line}: Operator '{node.op}' is not valid for type 'string'. "
                    f"Only '+' (concatenation) is allowed."
                )
                return None

            return left_type

        self.errors.append(f"Unknown expression node: {type(node).__name__}")
        return None


# ─── Public Entry ─────────────────────────────────────────────────────────────
def analyze(ast):
    analyzer = SemanticAnalyzer()
    errors   = analyzer.analyze(ast)
    return errors, analyzer.symbol_table
