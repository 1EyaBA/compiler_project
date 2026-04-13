"""
AST Pretty Printer
Converts an AST into a readable indented string for display.
"""

from .ast_nodes import (
    ProgramNode, DeclNode, AssignNode, BinOpNode,
    NumberNode, StringNode, IdentifierNode,
    IfNode, WhileNode, ConditionNode
)


def ast_to_lines(node, indent=0) -> list:
    pad   = "  " * indent
    lines = []

    if isinstance(node, ProgramNode):
        lines.append(f"{pad}Program")
        for stmt in node.statements:
            lines.extend(ast_to_lines(stmt, indent + 1))

    elif isinstance(node, DeclNode):
        lines.append(f"{pad}Declare  [{node.var_type}]  {node.name}")

    elif isinstance(node, AssignNode):
        lines.append(f"{pad}Assign  {node.name}  ←")
        lines.extend(ast_to_lines(node.expr, indent + 1))

    elif isinstance(node, BinOpNode):
        lines.append(f"{pad}BinOp  '{node.op}'")
        lines.extend(ast_to_lines(node.left,  indent + 1))
        lines.extend(ast_to_lines(node.right, indent + 1))

    elif isinstance(node, NumberNode):
        lines.append(f"{pad}Number  {node.value}")

    elif isinstance(node, StringNode):
        lines.append(f'{pad}String  "{node.value}"')

    elif isinstance(node, IdentifierNode):
        lines.append(f"{pad}Identifier  {node.name}")

    elif isinstance(node, IfNode):
        lines.append(f"{pad}If")
        lines.append(f"{pad}  condition:")
        lines.extend(ast_to_lines(node.condition, indent + 2))
        lines.append(f"{pad}  then:")
        for stmt in node.then_body:
            lines.extend(ast_to_lines(stmt, indent + 2))
        if node.else_body:
            lines.append(f"{pad}  else:")
            for stmt in node.else_body:
                lines.extend(ast_to_lines(stmt, indent + 2))

    elif isinstance(node, WhileNode):
        lines.append(f"{pad}While")
        lines.append(f"{pad}  condition:")
        lines.extend(ast_to_lines(node.condition, indent + 2))
        lines.append(f"{pad}  body:")
        for stmt in node.body:
            lines.extend(ast_to_lines(stmt, indent + 2))

    elif isinstance(node, ConditionNode):
        lines.append(f"{pad}Condition  '{node.op}'")
        lines.extend(ast_to_lines(node.left,  indent + 1))
        lines.extend(ast_to_lines(node.right, indent + 1))

    else:
        lines.append(f"{pad}Unknown({type(node).__name__})")

    return lines


def pretty_print(ast) -> str:
    return "\n".join(ast_to_lines(ast))
