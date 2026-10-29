# Lexical Analyser

Scanner for a simple variable declaration language (Compiler Construction class activity).

## Tokens

| Token type | Lexeme examples | Description |
|---|---|---|
| `INT` | `int` | keyword |
| `FLOAT` | `float` | keyword |
| `ID` | `x`, `total`, `count_1` | letter or `_`, followed by letters, digits, `_` |
| `NUM` | `10`, `42` | one or more digits |
| `ASSIGN` | `=` | assignment symbol |
| `PLUS` | `+` | addition symbol |
| `SEMI` | `;` | statement terminator |
| `EOF` | | end of input marker |

These are the terminals of the grammar:

```
Decl → Type id Init ;
Type → int | float
Init → = Expr | ε
Expr → num | id + num
```

## How it works

The scanner reads one character at a time (a hand-coded finite automaton):
- whitespace is skipped
- a letter or `_` starts an identifier or keyword; the lexeme is looked up in the keyword table
- a digit starts a number
- `=`, `+`, `;` are single-character tokens
- anything else raises a `LexicalError` with line and column

The lexer does **not** check grammar. `int x` (missing `;`) tokenizes fine; the parser rejects it.

## Run

```
python lexical_analyser.py "int total = x + 10;"
python lexical_analyser.py -f sample.txt
```

Example output:

```
<INT, 'int'>  (line 1, col 1)
<ID, 'total'>  (line 1, col 5)
<ASSIGN, '='>  (line 1, col 11)
<ID, 'x'>  (line 1, col 13)
<PLUS, '+'>  (line 1, col 15)
<NUM, '10'>  (line 1, col 17)
<SEMI, ';'>  (line 1, col 19)
<EOF, ''>  (line 1, col 20)
```

## Tests

```
python -m unittest test_lexical_analyser -v
```

## Next step

Recursive descent parser that consumes this token stream.
