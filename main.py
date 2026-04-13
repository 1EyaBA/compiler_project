"""
Mini Compiler — Streamlit Web App
INSAT Compilers Project — Spring 2026
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from compiler.lexer       import tokenize, spec_format
from compiler.parser      import parse, ParseError
from compiler.semantic    import analyze
from compiler.ast_printer import pretty_print

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mini Compiler",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Lucide SVG icons (inline) ────────────────────────────────────────────────
ICONS = {
    "scan":       '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>',
    "git-branch": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>',
    "shield":     '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "check":      '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "x":          '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "alert":      '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "file-code":  '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><polyline points="10 13 8 15 10 17"/><polyline points="14 13 16 15 14 17"/></svg>',
    "arrow-right":'<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "trash":      '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>',
    "pin":        '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="17" x2="12" y2="22"/><path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V17z"/></svg>',
    "book":       '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    "folder":     '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "table":      '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
    "skip":       '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/></svg>',
    "party":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5.8 11.3L2 22l10.7-3.79"/><path d="M4 3h.01"/><path d="M22 8h.01"/><path d="M15 2h.01"/><path d="M22 20h.01"/><path d="M22 2l-2.24.75a2.9 2.9 0 0 0-1.96 3.12c.1.86-.42 1.74-1.24 2.2l-.23.13c-.81.46-1.23 1.37-.94 2.26.21.66.02 1.38-.48 1.87l-.85.85"/></svg>',
    "warning":    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "school":     '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
    "valid-icon": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#2e8f6e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "invalid-icon":'<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "cpu-big":    '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "loop":       '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
}


# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .stApp { background: #f7f4ef; color: #1c1917; }

  section[data-testid="stSidebar"] {
    background: #fefcf8 !important;
    border-right: 1px solid #e8e0d4 !important;
  }
  .stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84rem !important;
    background: #fefcf8 !important;
    color: #1c1917 !important;
    border: 1.5px solid #d6cfc4 !important;
    border-radius: 10px !important;
    line-height: 1.7 !important;
  }
  .stTextArea textarea:focus {
    border-color: #c2763a !important;
    box-shadow: 0 0 0 3px rgba(194,118,58,0.12) !important;
  }
  .stTextArea label { font-weight: 600 !important; font-size: 0.85rem !important; color: #1c1917 !important; }

  .compiler-header { text-align:center; padding:2.8rem 0 1.2rem 0; }
  .compiler-header .icon-wrap {
    display:inline-flex; align-items:center; justify-content:center;
    background:#fff; border:1.5px solid #e8e0d4; border-radius:14px;
    width:56px; height:56px; margin-bottom:0.9rem;
    box-shadow:0 2px 10px rgba(0,0,0,0.06); color:#c2763a;
  }
  .compiler-header h1 {
    font-family:'DM Serif Display',serif; font-style:italic; font-weight:400;
    font-size:3rem; color:#1c1917; letter-spacing:-0.5px;
    margin-bottom:0.4rem; line-height:1.1;
  }
  .compiler-header h1 span { color:#c2763a; }
  .compiler-header p {
    color:#9c8f82; font-size:0.78rem; letter-spacing:3px;
    text-transform:uppercase; font-weight:500;
  }

  .pipeline {
    display:flex; align-items:center; justify-content:center;
    gap:0.4rem; margin:1.2rem 0 0.5rem 0; flex-wrap:wrap;
  }
  .pipe-step {
    display:inline-flex; align-items:center; gap:6px;
    background:#fff; border:1.5px solid #e8e0d4; border-radius:30px;
    padding:5px 14px; font-size:0.72rem; font-weight:600;
    letter-spacing:1.2px; text-transform:uppercase; color:#6b5e52;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
  }
  .pipe-step.active-lexer    { background:#fff8f0; border-color:#c2763a; color:#c2763a; }
  .pipe-step.active-parser   { background:#f5f0ff; border-color:#7c5cbf; color:#7c5cbf; }
  .pipe-step.active-semantic { background:#f0faf5; border-color:#2e8f6e; color:#2e8f6e; }
  .pipe-step.active-result   { background:#f0fdf4; border-color:#16a34a; color:#16a34a; }
  .pipe-arrow { color:#c9bdb3; display:inline-flex; align-items:center; }

  .phase-card {
    background:#fff; border:1.5px solid #e8e0d4; border-radius:14px;
    padding:1.4rem 1.6rem; margin-bottom:1rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.04);
  }
  .phase-title {
    display:flex; align-items:center; gap:8px;
    font-family:'DM Sans',sans-serif; font-weight:600; font-size:0.72rem;
    letter-spacing:3px; text-transform:uppercase;
    margin-bottom:1rem; padding-bottom:0.7rem; border-bottom:1px solid #f0ebe4;
  }
  .phase-lexer    { color:#c2763a; }
  .phase-parser   { color:#7c5cbf; }
  .phase-semantic { color:#2e8f6e; }

  .token-grid { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }
  .token-chip {
    display:inline-flex; align-items:center; gap:4px;
    font-family:'JetBrains Mono',monospace; font-size:0.72rem;
    padding:4px 11px; border-radius:20px; border:1.5px solid;
    white-space:nowrap; font-weight:600;
  }
  .chip-KEYWORD    { background:#fff8f0; color:#a85d20; border-color:#e8b88a; }
  .chip-IDENTIFIER { background:#f6f1ff; color:#5e3fa3; border-color:#c4a8ef; }
  .chip-NUMBER     { background:#f0fdf8; color:#1a7a5a; border-color:#86d5b8; }
  .chip-STRING_LIT { background:#fffbeb; color:#946c00; border-color:#f5d77a; }
  .chip-OPERATOR   { background:#fef2f2; color:#c0392b; border-color:#f5a8a8; }
  .chip-DELIMITER  { background:#f8f8f8; color:#6b6b6b; border-color:#cccccc; }

  .spec-box {
    font-family:'JetBrains Mono',monospace; font-size:0.78rem;
    background:#f5f0ff; color:#3b1f7a; border:1.5px solid #c4a8ef;
    border-radius:10px; padding:0.9rem 1.2rem; word-break:break-all;
    margin-top:0.8rem; line-height:1.7;
  }

  .ast-box {
    font-family:'JetBrains Mono',monospace; font-size:0.78rem;
    background:#fafaf8; color:#2d4a6e; border:1.5px solid #dde8f5;
    border-radius:10px; padding:1.1rem 1.3rem; white-space:pre;
    overflow-x:auto; max-height:380px; overflow-y:auto; line-height:1.8;
  }

  .badge-ok {
    display:inline-flex; align-items:center; gap:5px;
    background:#f0fdf4; color:#166534; border:1.5px solid #86efac;
    border-radius:20px; padding:4px 12px; font-size:0.78rem; font-weight:600;
  }
  .badge-err {
    display:inline-flex; align-items:center; gap:5px;
    background:#fff1f2; color:#9f1239; border:1.5px solid #fda4af;
    border-radius:20px; padding:4px 12px; font-size:0.78rem; font-weight:600;
  }

  .error-item {
    display:flex; align-items:flex-start; gap:8px;
    background:#fff8f8; border-left:3px solid #e05252;
    border-radius:6px; padding:9px 14px; margin:5px 0;
    font-family:'JetBrains Mono',monospace; font-size:0.76rem;
    color:#8b2020; line-height:1.5;
  }
  .error-item svg { flex-shrink:0; margin-top:2px; }

  .sym-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:7px 14px; border-radius:8px; margin:4px 0;
    font-family:'JetBrains Mono',monospace; font-size:0.8rem; border:1px solid;
  }
  .sym-int    { background:#f0f7ff; color:#1d4ed8; border-color:#bfdbfe; }
  .sym-string { background:#fdf4ff; color:#7e22ce; border-color:#e9d5ff; }
  .sym-name   { font-weight:700; }
  .sym-type   { font-size:0.68rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; opacity:0.65; }
  .sym-scope  { font-size:0.65rem; opacity:0.5; margin-left:0.5rem; }

  div.stButton > button {
    width:100%; background:#1c1917; color:#f7f4ef; border:none;
    border-radius:10px; font-family:'DM Sans',sans-serif; font-weight:600;
    font-size:0.9rem; padding:0.7rem 1rem; letter-spacing:0.5px;
    transition:background 0.2s, transform 0.1s; cursor:pointer;
  }
  div.stButton > button:hover { background:#c2763a; transform:translateY(-1px); }

  hr { border:none; border-top:1px solid #e8e0d4 !important; margin:1.5rem 0 !important; }
  details { background:#fafaf8; border:1px solid #e8e0d4; border-radius:8px; padding:0 0.5rem; }

  .sidebar-section {
    display:flex; align-items:center; gap:7px;
    font-size:0.7rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#9c8f82; margin:1rem 0 0.4rem 0;
  }
  .sub-label {
    display:flex; align-items:center; gap:5px;
    font-size:0.7rem; font-weight:700; margin:0.6rem 0 0.3rem 0;
  }

  .example-hint {
    display:flex; align-items:center; gap:6px;
    font-size:0.78rem; color:#9c8f82; margin-bottom:0.4rem;
  }
  .example-hint strong { color:#c2763a; }

  .empty-state { text-align:center; padding:4rem 0 3rem 0; }
  .empty-state .icon-wrap {
    display:inline-flex; align-items:center; justify-content:center;
    width:64px; height:64px; background:#fff; border:1.5px solid #e8e0d4;
    border-radius:16px; margin-bottom:1rem; color:#c9bdb3;
    box-shadow:0 2px 10px rgba(0,0,0,0.05);
  }
  .empty-state p { color:#9c8f82; font-size:0.95rem; line-height:1.6; }
  .empty-state strong { color:#c2763a; }

  .result-ok  { display:flex; align-items:center; gap:8px; background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:14px 18px; color:#166534; font-weight:600; }
  .result-err { display:flex; align-items:center; gap:8px; background:#fff1f2; border:1.5px solid #fda4af; border-radius:12px; padding:14px 18px; color:#9f1239; font-weight:600; }
  .result-warn{ display:flex; align-items:center; gap:8px; background:#fffbeb; border:1.5px solid #fde68a; border-radius:12px; padding:14px 18px; color:#92400e; font-weight:600; }
  .skipped    { display:flex; align-items:center; gap:6px; color:#9c8f82; font-size:0.85rem; }
  .sym-header { margin:1rem 0 0.4rem 0; font-weight:600; font-size:0.82rem; display:flex; align-items:center; gap:6px; color:#1c1917; }
</style>
""", unsafe_allow_html=True)


# ─── Example Programs ─────────────────────────────────────────────────────────
EXAMPLES = {
    "Arithmetic & If": {
        "valid": True,
        "desc": "Variables entières, opérations, condition simple",
        "code": "int x;\nint y;\nx = 5 + 2;\ny = x * 3;\nif x > 4 then {\n    x = x - 1;\n}"
    },
    "While loop": {
        "valid": True,
        "desc": "Boucle while avec compteur (nouvelle fonctionnalité)",
        "code": "int x;\nint sum;\nx = 5;\nsum = 0;\nwhile x > 0 do {\n    sum = sum + x;\n    x = x - 1;\n}"
    },
    "Opérateurs étendus": {
        "valid": True,
        "desc": ">=, <=, ==, != dans les conditions",
        "code": "int x;\nint y;\nx = 10;\ny = 10;\nif x >= y then {\n    x = x - 1;\n}\nif x != y then {\n    y = y + 1;\n}\nif x == 9 then {\n    x = 0;\n}"
    },
    "Strings": {
        "valid": True,
        "desc": "Déclaration et concaténation de chaînes",
        "code": 'string firstName;\nstring lastName;\nstring fullName;\nfirstName = "Alice";\nlastName = "Smith";\nfullName = firstName + lastName;'
    },
    "If / Else": {
        "valid": True,
        "desc": "Branchement conditionnel avec else",
        "code": "int a;\nint b;\na = 10;\nb = 5;\nif a > b then {\n    a = a - 1;\n} else {\n    b = b + 1;\n}"
    },
    "Expressions complexes": {
        "valid": True,
        "desc": "Expressions avec parenthèses et priorité",
        "code": "int result;\nint temp;\nresult = (3 + 4) * 2;\ntemp = result - 1;\nif temp > 10 then {\n    result = result + temp;\n} else {\n    result = temp * 2;\n}"
    },
    "While + If imbriqué": {
        "valid": True,
        "desc": "Boucle while avec if à l'intérieur",
        "code": "int x;\nint y;\nx = 10;\ny = 0;\nwhile x > 0 do {\n    x = x - 1;\n    if x > 5 then {\n        y = y + 1;\n    }\n}"
    },
    "Type Mismatch": {
        "valid": False,
        "desc": "Affectation d'un string à un int",
        "code": 'int x;\nx = "hello";'
    },
    "Variable non declaree": {
        "valid": False,
        "desc": "Utilisation avant déclaration",
        "code": "int x;\nx = y + 1;"
    },
    "Scope isolation": {
        "valid": False,
        "desc": "Variable de bloc non visible à l'extérieur",
        "code": "int x;\nx = 1;\nif x > 0 then {\n    int inner;\n    inner = 42;\n}\ninner = 0;"
    },
    "Types mixtes dans expr": {
        "valid": False,
        "desc": "Addition int + string interdite",
        "code": 'int x;\nstring s;\nx = 5;\ns = "hi";\nx = x + s;'
    },
    "Double declaration": {
        "valid": False,
        "desc": "Déclarer la même variable deux fois",
        "code": "int x;\nint x;\nx = 5;"
    },
    "Operateur invalide sur string": {
        "valid": False,
        "desc": "Soustraction de strings interdite",
        "code": 'string a;\nstring b;\na = "hello";\nb = "world";\na = a - b;'
    },
    "Erreur syntaxique": {
        "valid": False,
        "desc": "Point-virgule manquant",
        "code": "int x\nx = 5;"
    },
    "While sans do": {
        "valid": False,
        "desc": "Mot-clé 'do' manquant dans while",
        "code": "int x;\nx = 3;\nwhile x > 0 {\n    x = x - 1;\n}"
    },
}

# ─── Session State ────────────────────────────────────────────────────────────
if "code" not in st.session_state:
    st.session_state["code"] = EXAMPLES["Arithmetic & If"]["code"]
if "selected_example" not in st.session_state:
    st.session_state["selected_example"] = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div class="sidebar-section">{ICONS["folder"]} Exemples de programmes</div>',
        unsafe_allow_html=True
    )

    valid_examples   = {k: v for k, v in EXAMPLES.items() if v["valid"]}
    invalid_examples = {k: v for k, v in EXAMPLES.items() if not v["valid"]}

    st.markdown(
        f'<div class="sub-label" style="color:#2e8f6e;">{ICONS["valid-icon"]} Programmes valides</div>',
        unsafe_allow_html=True
    )
    for name, info in valid_examples.items():
        if st.button(name, key=f"ex_{name}", help=info["desc"], use_container_width=True):
            st.session_state["code"] = info["code"]
            st.session_state["selected_example"] = name
            st.rerun()

    st.markdown(
        f'<div class="sub-label" style="color:#c0392b;margin-top:0.8rem;">{ICONS["invalid-icon"]} Programmes avec erreurs</div>',
        unsafe_allow_html=True
    )
    for name, info in invalid_examples.items():
        if st.button(name, key=f"ex_{name}", help=info["desc"], use_container_width=True):
            st.session_state["code"] = info["code"]
            st.session_state["selected_example"] = name
            st.rerun()

    st.markdown("---")
    st.markdown(
        f'<div class="sidebar-section">{ICONS["book"]} Grammaire du langage</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
```
<program>  ::= <stmt>*
<stmt>     ::= <decl>
             | <assign>
             | <if>
             | <while>
<decl>     ::= (int|string) ID ;
<assign>   ::= ID = <expr> ;
<if>       ::= if <cond> then { <stmt>* }
               (else { <stmt>* })?
<while>    ::= while <cond> do { <stmt>* }
<cond>     ::= <expr> <cmp_op> <expr>
<cmp_op>   ::= > | < | = | == | >= | <= | !=
<expr>     ::= <term> ((+|-) <term>)*
<term>     ::= <factor> ((*|/) <factor>)*
<factor>   ::= NUMBER | STRING | ID
             | ( <expr> )
```
""")
    st.markdown("---")
    st.markdown(
        f'<div class="sidebar-section">{ICONS["school"]} INSAT — Spring 2026</div>',
        unsafe_allow_html=True
    )
    st.caption("Compilers Course Project")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="compiler-header">
  <div class="icon-wrap">{ICONS["cpu-big"]}</div>
  <h1>Mini <span>Compiler</span></h1>
  <p>Lexer · Parser · Semantic Analyzer</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="pipeline">
  <div class="pipe-step">{ICONS["file-code"]} Source Code</div>
  <div class="pipe-arrow">{ICONS["arrow-right"]}</div>
  <div class="pipe-step active-lexer">{ICONS["scan"]} Lexer</div>
  <div class="pipe-arrow">{ICONS["arrow-right"]}</div>
  <div class="pipe-step active-parser">{ICONS["git-branch"]} Parser</div>
  <div class="pipe-arrow">{ICONS["arrow-right"]}</div>
  <div class="pipe-step active-semantic">{ICONS["shield"]} Semantic</div>
  <div class="pipe-arrow">{ICONS["arrow-right"]}</div>
  <div class="pipe-step active-result">{ICONS["check"]} Result</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Code Input ───────────────────────────────────────────────────────────────
if st.session_state.get("selected_example"):
    ex   = st.session_state["selected_example"]
    desc = EXAMPLES[ex]["desc"]
    st.markdown(
        f'<div class="example-hint">{ICONS["pin"]} Exemple chargé : <strong>{ex}</strong> — {desc}</div>',
        unsafe_allow_html=True
    )

code = st.text_area(
    "Code source",
    value=st.session_state["code"],
    height=180,
    help="Écrivez votre programme ici. Sélectionnez un exemple dans la barre latérale ou tapez le vôtre."
)
st.session_state["code"] = code

col_run, col_clear = st.columns([3, 1])
with col_run:
    run_all = st.button("Compiler — Lancer toutes les phases", key="run_all")
with col_clear:
    if st.button("Effacer", key="clear"):
        st.session_state["code"] = ""
        st.session_state["selected_example"] = None
        st.rerun()

st.markdown("---")

# ─── Run Pipeline ─────────────────────────────────────────────────────────────
if run_all and code.strip():
    source = code

    # ── PHASE 1: LEXER ────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="phase-card"><div class="phase-title phase-lexer">{ICONS["scan"]} Phase 1 — Analyse Lexicale</div>',
        unsafe_allow_html=True
    )
    try:
        tokens = tokenize(source)
        st.markdown(f'<span class="badge-ok">{ICONS["check"]} {len(tokens)} tokens trouvés</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Token chips
        chip_html = '<div class="token-grid">'
        label_map = {'KEYWORD':'KW','IDENTIFIER':'ID','NUMBER':'NUM','STRING_LIT':'STR','OPERATOR':'OP','DELIMITER':'DL'}
        for tok in tokens:
            label = label_map.get(tok.type, tok.type)
            chip_html += f'<span class="token-chip chip-{tok.type}" title="Ligne {tok.line}">{label}: {tok.value}</span>'
        chip_html += '</div>'
        st.markdown(chip_html, unsafe_allow_html=True)

        # Spec-format token stream (as per project spec examples)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Format spec du projet :**", unsafe_allow_html=False)
        st.markdown(f'<div class="spec-box">{spec_format(tokens)}</div>', unsafe_allow_html=True)

        with st.expander("Table complète des tokens"):
            c1, c2, c3 = st.columns([2, 3, 1])
            c1.markdown("**Type**"); c2.markdown("**Valeur**"); c3.markdown("**Ligne**")
            for tok in tokens:
                a, b, c_ = st.columns([2, 3, 1])
                a.code(tok.type); b.code(repr(tok.value)); c_.write(str(tok.line))

        lexer_ok = True
    except SyntaxError as e:
        st.markdown(f'<span class="badge-err">{ICONS["x"]} Erreur Lexicale</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="error-item">{ICONS["alert"]} {e}</div>', unsafe_allow_html=True)
        lexer_ok = False
        tokens   = []
    st.markdown('</div>', unsafe_allow_html=True)

    # ── PHASE 2: PARSER ───────────────────────────────────────────────────────
    st.markdown(
        f'<div class="phase-card"><div class="phase-title phase-parser">{ICONS["git-branch"]} Phase 2 — Analyse Syntaxique (AST)</div>',
        unsafe_allow_html=True
    )
    if lexer_ok:
        try:
            ast_tree = parse(tokens)
            st.markdown(f'<span class="badge-ok">{ICONS["check"]} AST construit avec succès</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="ast-box">{pretty_print(ast_tree)}</div>', unsafe_allow_html=True)
            parser_ok = True
        except ParseError as e:
            st.markdown(f'<span class="badge-err">{ICONS["x"]} Erreur Syntaxique</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="error-item">{ICONS["alert"]} {e}</div>', unsafe_allow_html=True)
            parser_ok = False
            ast_tree  = None
    else:
        st.markdown(f'<div class="skipped">{ICONS["skip"]} Ignoré — corrigez les erreurs lexicales d\'abord.</div>', unsafe_allow_html=True)
        parser_ok = False
        ast_tree  = None
    st.markdown('</div>', unsafe_allow_html=True)

    # ── PHASE 3: SEMANTIC ─────────────────────────────────────────────────────
    st.markdown(
        f'<div class="phase-card"><div class="phase-title phase-semantic">{ICONS["shield"]} Phase 3 — Analyse Sémantique</div>',
        unsafe_allow_html=True
    )
    if parser_ok and ast_tree:
        errors, sym_table = analyze(ast_tree)
        if not errors:
            st.markdown(f'<span class="badge-ok">{ICONS["check"]} Aucune erreur sémantique</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge-err">{ICONS["x"]} {len(errors)} erreur(s) sémantique(s)</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for err in errors:
                st.markdown(f'<div class="error-item">{ICONS["alert"]} {err}</div>', unsafe_allow_html=True)

        # Symbol table with scope levels
        st.markdown(f'<div class="sym-header">{ICONS["table"]} Table des symboles</div>', unsafe_allow_html=True)
        variables = sym_table.all_variables()
        if variables:
            for var_name, info in variables.items():
                var_type  = info['type']
                var_level = info['level']
                cls       = "sym-int" if var_type == "int" else "sym-string"
                scope_label = "global" if var_level == 0 else f"scope {var_level}"
                st.markdown(
                    f'<div class="sym-row {cls}">'
                    f'<span class="sym-name">{var_name}</span>'
                    f'<span>'
                    f'<span class="sym-type">{var_type}</span>'
                    f'<span class="sym-scope">({scope_label})</span>'
                    f'</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.caption("Aucune variable déclarée.")
    else:
        st.markdown(f'<div class="skipped">{ICONS["skip"]} Ignoré — corrigez les erreurs syntaxiques d\'abord.</div>', unsafe_allow_html=True)
        errors = []
    st.markdown('</div>', unsafe_allow_html=True)

    # ── FINAL RESULT ──────────────────────────────────────────────────────────
    st.markdown("---")
    if lexer_ok and parser_ok:
        if not errors:
            st.markdown(f'<div class="result-ok">{ICONS["party"]} Compilation réussie — aucune erreur détectée.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-err">{ICONS["x"]} Compilation échouée — {len(errors)} erreur(s) sémantique(s) détectée(s).</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="result-err">{ICONS["x"]} Compilation échouée — corrigez les erreurs ci-dessus.</div>', unsafe_allow_html=True)

elif run_all and not code.strip():
    st.markdown(f'<div class="result-warn">{ICONS["warning"]} Veuillez saisir du code source avant de compiler.</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="empty-state">
      <div class="icon-wrap">{ICONS["cpu-big"]}</div>
      <p>Sélectionnez un exemple dans la barre latérale ou écrivez du code,<br>puis cliquez sur <strong>Compiler</strong> pour lancer les trois phases.</p>
    </div>
    """, unsafe_allow_html=True)
