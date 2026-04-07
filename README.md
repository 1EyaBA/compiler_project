# ⚙️ Mini Compiler — INSAT Spring 2026

A full compiler pipeline for a custom programming language, built with Python and Streamlit.

## Features
- **Lexer** — tokenizes source code into typed tokens
- **Parser** — builds an Abstract Syntax Tree (AST) using recursive descent
- **Semantic Analyzer** — type checking, scope resolution, symbol table
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
│   ├── lexer.py             # Milestone 1: Lexer
│   ├── parser.py            # Milestone 2: Parser
│   ├── semantic.py          # Milestone 3: Semantic Analyzer
│   ├── ast_nodes.py         # AST node classes
│   ├── ast_printer.py       # AST pretty printer
│   └── symbol_table.py      # Symbol table
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_semantic.py
├── examples/                # Sample programs
└── requirements.txt
```

## Team
INSAT — Compilers Course — Spring 2026
