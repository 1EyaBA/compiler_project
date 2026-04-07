"""
Symbol Table
Tracks variable names, types, and declaration status.
"""


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]   # stack of scopes; index 0 = global

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name: str, var_type: str, line=None):
        current_scope = self.scopes[-1]
        if name in current_scope:
            raise Exception(
                f"Line {line}: Variable '{name}' is already declared in this scope."
            )
        current_scope[name] = var_type

    def lookup(self, name: str, line=None) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Line {line}: Undeclared variable '{name}'.")

    def is_declared(self, name: str) -> bool:
        return any(name in scope for scope in reversed(self.scopes))

    def all_variables(self) -> dict:
        """Return flat view of all variables for display."""
        result = {}
        for scope in self.scopes:
            result.update(scope)
        return result

    def __repr__(self):
        return f"SymbolTable({self.scopes})"
