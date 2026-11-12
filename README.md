# Compiler Front End

A lexer and syntax checker for a small variable declaration language, and a calculator driven by a syntax-directed definition. Written in Python with no dependencies.

Example declarations:

```
int x;
float total;
int count = 10;
int total = x + 10;
```

- `lexical_analyser.py` turns source text into tokens with regular expressions and reports invalid tokens with their line and column.
- `syntax_analyser.py` checks the tokens against the grammar: it proves valid input with a leftmost derivation, or reports the rule that invalid input breaks.
- `sdd_calculator.py` evaluates `+` and `*` expressions such as `(3+4)*(5+6)` and prints the annotated parse tree.

## Grammar

```
<program> → <decl> <program> | <decl>
<decl>    → <type> id <init> ;
<type>    → int | float
<init>    → = <expr> | ε
<expr>    → <expr> + <term> | <term>
<term>    → id | number
```

Terminals, non-terminals, sample derivations and rejected inputs are in [Context Free Grammar.md](Context%20Free%20Grammar.md).

## Tokens

Each terminal of the grammar is one token:

| Token | Lexeme examples | Description |
|---|---|---|
| `INT` | `int` | keyword |
| `FLOAT` | `float` | keyword |
| `ID` | `x`, `total`, `count_1` | identifier |
| `NUMBER` | `10`, `42` | whole number |
| `ASSIGN` | `=` | assignment symbol |
| `PLUS` | `+` | addition symbol |
| `SEMI` | `;` | statement terminator |
| `EOF` | | end of input marker (added by the lexer) |

## Reserved keywords

`int` and `float`. They also fit the identifier pattern, so every identifier lexeme is looked up in the keyword table (`KEYWORDS`). That is why `int` becomes `INT` but `integer` stays an `ID`.

## Regular expressions

`TOKEN_RULES` in `lexical_analyser.py` holds one regular expression per kind of lexeme. At each position the rules are tried in order and the first match wins:

| Rule | Regular expression | Result |
|---|---|---|
| newline | `\n` | skipped (line count + 1) |
| whitespace | `[ \t\r]+` | skipped |
| bad number | `[0-9]+[A-Za-z_][A-Za-z0-9_]*` | lexical error, so `12abc` is not split into `12` and `abc` |
| `NUMBER` | `[0-9]+` | token |
| `ID` | `[A-Za-z_][A-Za-z0-9_]*` | token, or `INT` / `FLOAT` if it is a keyword |
| `ASSIGN` | `=` | token |
| `PLUS` | `\+` | token |
| `SEMI` | `;` | token |
| anything else | `.` | lexical error |

## Lexical errors

Invalid tokens are reported during lexical analysis, with line and column:

| Input | Output |
|---|---|
| `int x = 2 * 3;` | `Lexical error at line 1, column 11: unexpected character '*'` |
| `int x @ 5;` | `Lexical error at line 1, column 7: unexpected character '@'` |
| `int x = 12abc;` | `Lexical error at line 1, column 9: invalid token '12abc'` |

Breaking a grammar rule is **not** a lexical error. `int x` (missing `;`) and `= x;` (missing type) contain only valid tokens, so the lexer accepts them. They are syntax errors, caught by the syntax checker (see [Valid or not valid?](#valid-or-not-valid)).

## Usage

Requires [uv](https://docs.astral.sh/uv/).

### Lexer

```
uv run lexical_analyser.py "int total = x + 10;"
uv run lexical_analyser.py -f sample.txt
```

Example output:

```
<INT, 'int'>  (line 1, col 1)
<ID, 'total'>  (line 1, col 5)
<ASSIGN, '='>  (line 1, col 11)
<ID, 'x'>  (line 1, col 13)
<PLUS, '+'>  (line 1, col 15)
<NUMBER, '10'>  (line 1, col 17)
<SEMI, ';'>  (line 1, col 19)
<EOF, ''>  (line 1, col 20)
```

### Valid or not valid?

`syntax_analyser.py` checks the lexer's tokens against the grammar:

- **VALID** input is proven with a leftmost derivation from `<program>`, with the production used at each step.
- **NOT VALID** input shows where it fails and which rule it violates.

```
uv run syntax_analyser.py "int total = x + 10;"
uv run syntax_analyser.py -f sample.txt
```

Example output:

```
  Leftmost derivation           Production used
  <program>
⇒ <decl>                        <program> → <decl>
⇒ <type> id <init> ;            <decl> → <type> id <init> ;
⇒ int id <init> ;               <type> → int
⇒ int id = <expr> ;             <init> → = <expr>
⇒ int id = <expr> + <term> ;    <expr> → <expr> + <term>
⇒ int id = <term> + <term> ;    <expr> → <term>
⇒ int id = id + <term> ;        <term> → id
⇒ int id = id + number ;        <term> → number

VALID: int total = x + 10 ;
```

| Input | Output |
|---|---|
| `int x` | `NOT VALID: Syntax error at line 1, column 6: expected '=' or ';', found end of input`<br>`Rule violated: <decl> → <type> id <init> ;` |
| `int x =;` | `NOT VALID: Syntax error at line 1, column 8: expected id or number, found ';'`<br>`Rule violated: <init> → = <expr>` |
| `int x = 2 * 3;` | `NOT VALID: Lexical error at line 1, column 11: unexpected character '*'` |

## Syntax-directed calculator

A syntax-directed definition specifies how a grammar is interpreted: each production gets a semantic rule that computes an attribute. `sdd_calculator.py` uses one to evaluate expressions with `+`, `*`, parentheses and whole numbers. The attribute `val` is synthesized, so each node's value comes from its children.

| Production | Semantic rule |
|---|---|
| `L → E n` | `L.val = E.val` |
| `E → E1 + T` | `E.val = E1.val + T.val` |
| `E → T` | `E.val = T.val` |
| `T → T1 * F` | `T.val = T1.val * F.val` |
| `T → F` | `T.val = F.val` |
| `F → ( E )` | `F.val = E.val` |
| `F → digit` | `F.val = digit.lexval` |

`n` marks the end of the line, and `digit.lexval` is the number's value from the lexer.

```
uv run sdd_calculator.py "(3+4)*(5+6)"
```

It prints the annotated parse tree, with the semantic rule applied at each node:

```
Annotated parse tree                                    Semantic rule
L.val = 77                                              L.val = E.val
├── E.val = 77                                          E.val = T.val
│   └── T.val = 77                                      T.val = T1.val * F.val
│       ├── T.val = 7                                   T.val = F.val
│       │   └── F.val = 7                               F.val = E.val
│       │       ├── (
│       │       ├── E.val = 7                           E.val = E1.val + T.val
│       │       │   ├── E.val = 3                       E.val = T.val
│       │       │   │   └── T.val = 3                   T.val = F.val
│       │       │   │       └── F.val = 3               F.val = digit.lexval
│       │       │   │           └── digit.lexval = 3
│       │       │   ├── +
│       │       │   └── T.val = 4                       T.val = F.val
│       │       │       └── F.val = 4                   F.val = digit.lexval
│       │       │           └── digit.lexval = 4
│       │       └── )
│       ├── *
│       └── F.val = 11                                  F.val = E.val
│           ├── (
│           ├── E.val = 11                              E.val = E1.val + T.val
│           │   ├── E.val = 5                           E.val = T.val
│           │   │   └── T.val = 5                       T.val = F.val
│           │   │       └── F.val = 5                   F.val = digit.lexval
│           │   │           └── digit.lexval = 5
│           │   ├── +
│           │   └── T.val = 6                           T.val = F.val
│           │       └── F.val = 6                       F.val = digit.lexval
│           │           └── digit.lexval = 6
│           └── )
└── n

(3+4)*(5+6) = 77
```

Invalid expressions are reported the same way as in the syntax checker, e.g. `(3+4` gives `NOT VALID: Syntax error at line 1, column 5: expected '+', '*' or ')', found end of line` and `Rule violated: F → ( E )`.

## Tests

```
uv run python -m unittest -v
```
