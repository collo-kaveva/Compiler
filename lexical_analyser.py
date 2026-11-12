"""
Lexical Analyser (Scanner) for a small variable declaration language.

Design:
    1. Grammar (see "Context Free Grammar.md"):
           <program> → <decl> <program> | <decl>
           <decl>    → <type> id <init> ;
           <type>    → int | float
           <init>    → = <expr> | ε
           <expr>    → <expr> + <term> | <term>
           <term>    → id | number
    2. Tokens, one per terminal:  int  float  id  number  =  +  ;
    3. Reserved keywords:  int  float
    4. Regular expressions:  TOKEN_RULES, tried in order at each position
    5. Invalid tokens raise a LexicalError with line and column

Usage:
    uv run lexical_analyser.py "int x = 10;"
    uv run lexical_analyser.py -f sample.txt
"""

import re
import sys
from dataclasses import dataclass

# Token types (one per terminal in the grammar)
INT, FLOAT = "INT", "FLOAT"
ID, NUMBER = "ID", "NUMBER"
ASSIGN, PLUS, SEMI = "ASSIGN", "PLUS", "SEMI"
EOF = "EOF"

# Reserved keywords. They fit the ID pattern, so every ID lexeme is looked up here.
KEYWORDS = {"int": INT, "float": FLOAT}

# Regular expression for each kind of lexeme. Order matters: the first match wins.
TOKEN_RULES = [
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r]+"),
    ("BAD_NUMBER", r"[0-9]+[A-Za-z_][A-Za-z0-9_]*"),  # e.g. 12abc
    (NUMBER, r"[0-9]+"),
    (ID, r"[A-Za-z_][A-Za-z0-9_]*"),
    (ASSIGN, r"="),
    (PLUS, r"\+"),
    (SEMI, r";"),
    ("MISMATCH", r"."),
]
TOKEN_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_RULES)
)


class LexicalError(Exception):
    """Raised when the input contains something that is not a valid token."""

    def __init__(self, message, line, column):
        super().__init__(f"Lexical error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column


@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    column: int

    def __str__(self):
        return f"<{self.type}, '{self.lexeme}'>  (line {self.line}, col {self.column})"


class Lexer:
    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.line = 1
        self.line_start = 0

    def next_token(self):
        while self.pos < len(self.src):
            match = TOKEN_PATTERN.match(self.src, self.pos)
            kind, text = match.lastgroup, match.group()
            col = self.pos - self.line_start + 1
            self.pos = match.end()

            if kind == "NEWLINE":
                self.line += 1
                self.line_start = self.pos
            elif kind == "BAD_NUMBER":
                raise LexicalError(f"invalid token '{text}'", self.line, col)
            elif kind == "MISMATCH":
                raise LexicalError(f"unexpected character '{text}'", self.line, col)
            elif kind == ID:
                return Token(KEYWORDS.get(text, ID), text, self.line, col)
            elif kind != "SKIP":
                return Token(kind, text, self.line, col)

        return Token(EOF, "", self.line, self.pos - self.line_start + 1)

    def tokenize(self):
        """Return the full list of tokens, ending with an EOF token."""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == EOF:
                return tokens


def read_source(args):
    """Input text from the command line: a quoted string, or -f FILE."""
    if args[0] != "-f":
        return " ".join(args)
    if len(args) < 2:
        sys.exit("Error: -f needs a file name")
    try:
        with open(args[1], encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        sys.exit(f"Error: {e}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    source = read_source(args)

    try:
        for tok in Lexer(source).tokenize():
            print(tok)
    except LexicalError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
