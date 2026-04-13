# ⚙️ Mini Compiler — INSAT Spring 2026

A full compiler pipeline for a custom programming language, built with Python and Streamlit.

## Features
- **Lexer** — tokenizes source code; outputs spec-format stream `[ID('x'), '=', NUM(5), ...]`
- **Parser** — builds an Abstract Syntax Tree (AST) using recursive descent
- **Semantic Analyzer** — type checking, scope resolution, symbol table with scope levels
- **Web UI** — interactive Streamlit app with colored token display, AST viewer, and error reporting

## Language Supported

```
int x;
string name;
x = 5 + 2 * 3;
name = "Alice";

if x > 4 then {
    x = x - 1;
} else {
    x = x + 1;
}

while x >= 1 do {
    x = x - 1;
}
```

### Supported operators
| Category    | Operators              |
|-------------|------------------------|
| Arithmetic  | `+` `-` `*` `/`        |
| Comparison  | `>` `<` `=` `==` `>=` `<=` `!=` |
| Assignment  | `=`                    |

### Formal Grammar (BNF)

```
<program>  ::= <stmt>*
<stmt>     ::= <decl> | <assign> | <if> | <while>
<decl>     ::= (int|string) ID ;
<assign>   ::= ID = <expr> ;
<if>       ::= if <cond> then { <stmt>* } (else { <stmt>* })?
<while>    ::= while <cond> do { <stmt>* }
<cond>     ::= <expr> <cmp_op> <expr>
<cmp_op>   ::= > | < | = | == | >= | <= | !=
<expr>     ::= <term> ((+|-) <term>)*
<term>     ::= <factor> ((*|/) <factor>)*
<factor>   ::= NUMBER | STRING | ID | ( <expr> )
```

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run main.py
```

## Run Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
compiler_project/
├── main.py                  # Streamlit UI
├── compiler/
│   ├── lexer.py             # Milestone 1: Lexer + spec_format()
│   ├── parser.py            # Milestone 2: Parser (if, while, extended ops)
│   ├── semantic.py          # Milestone 3: Semantic Analyzer
│   ├── ast_nodes.py         # AST node classes (incl. WhileNode)
│   ├── ast_printer.py       # AST pretty printer
│   └── symbol_table.py      # Symbol table with scope levels
├── tests/
│   ├── test_lexer.py        # Lexer tests incl. >=, <=, !=, ==, spec_format
│   ├── test_parser.py       # Parser tests incl. while, extended ops
│   └── test_semantic.py     # Semantic tests incl. scope isolation, while
├── examples/
│   ├── valid_arithmetic.txt
│   ├── valid_strings.txt
│   ├── if_else.txt
│   ├── while_loop.txt       # NEW
│   ├── extended_ops.txt     # NEW
│   ├── scope_error.txt      # NEW
│   ├── type_error.txt
│   └── undeclared_var.txt
└── requirements.txt
```

## Changelog

### v2.0 (Spring 2026 — improvements)
- ✅ Added `while ... do { }` loop support (parser + semantic + AST + UI)
- ✅ Added extended comparison operators: `==`, `>=`, `<=`, `!=`
- ✅ Added `spec_format()` to display token streams in project-spec format
- ✅ Scope isolation: variables declared inside blocks are not visible outside
- ✅ Symbol table now tracks and displays scope level (global / block)
- ✅ Fixed multi-char operators (`>=`, `<=` not split into two tokens)
- ✅ Added `while`/`do` as reserved keywords in lexer
- ✅ Expanded test suite: 40+ tests covering all new features

## Team
INSAT — Compilers Course — Spring 2026
