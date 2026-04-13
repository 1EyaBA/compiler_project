"""
AST Node Definitions
Each class represents a node in the Abstract Syntax Tree.
"""

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class DeclNode:
    def __init__(self, var_type, name, line=None):
        self.var_type = var_type
        self.name = name
        self.line = line

    def __repr__(self):
        return f"Decl({self.var_type}, {self.name})"


class AssignNode:
    def __init__(self, name, expr, line=None):
        self.name = name
        self.expr = expr
        self.line = line

    def __repr__(self):
        return f"Assign({self.name}, {self.expr})"


class BinOpNode:
    def __init__(self, left, op, right, line=None):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def __repr__(self):
        return f"BinOp({self.left} {self.op} {self.right})"


class NumberNode:
    def __init__(self, value, line=None):
        self.value = int(value)
        self.line = line

    def __repr__(self):
        return f"NUM({self.value})"


class StringNode:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"STR({self.value})"


class IdentifierNode:
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"ID({self.name})"


class IfNode:
    def __init__(self, condition, then_body, else_body=None, line=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body
        self.line = line

    def __repr__(self):
        return f"If({self.condition}, then={self.then_body}, else={self.else_body})"


class WhileNode:
    """Represents a while loop: while <condition> do { <stmt_list> }"""
    def __init__(self, condition, body, line=None):
        self.condition = condition
        self.body = body
        self.line = line

    def __repr__(self):
        return f"While({self.condition}, body={self.body})"


class ConditionNode:
    def __init__(self, left, op, right, line=None):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def __repr__(self):
        return f"Cond({self.left} {self.op} {self.right})"
