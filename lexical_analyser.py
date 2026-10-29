"""
Lexical Analyser (Scanner) for a simple variable declaration language.

Token set (the terminals of the grammar):
    int  float  id  num  =  +  ;

Grammar this scanner supports:
    Decl → Type id Init ;
    Type → int | float
    Init → = Expr | ε
    Expr → num | id + num

The scanner is written as a hand-coded finite automaton: it reads one
character at a time and decides which token is being formed.

Usage:
    python lexical_analyser.py "int x = 10;"
    python lexical_analyser.py -f sample.txt
"""

import sys
from dataclasses import dataclass

# Token types (one per terminal in the grammar)
INT, FLOAT = "INT", "FLOAT"
ID, NUM = "ID", "NUM"
ASSIGN, PLUS, SEMI = "ASSIGN", "PLUS", "SEMI"
EOF = "EOF"

# Reserved keywords. These are never treated as identifiers.
KEYWORDS = {"int": INT, "float": FLOAT}

# Single-character tokens
SYMBOLS = {"=": ASSIGN, "+": PLUS, ";": SEMI}


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
        self.col = 1

    # ---- helpers -------------------------------------------------------
    def _peek(self):
        return self.src[self.pos] if self.pos < len(self.src) else ""

    def _advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace(self):
        while self._peek() and self._peek() in " \t\r\n":
            self._advance()

    # ---- token recognisers --------------------------------------------
    def _identifier_or_keyword(self, line, col):
        # State: first char is a letter or '_'.  Loop: letters, digits, '_'.
        text = ""
        while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
            text += self._advance()
        return Token(KEYWORDS.get(text, ID), text, line, col)

    def _number(self, line, col):
        # State: first char is a digit.  Loop: more digits.
        text = ""
        while self._peek() and self._peek().isdigit():
            text += self._advance()
        # A number glued to letters (e.g. 12abc) is an invalid token.
        if self._peek() and (self._peek().isalpha() or self._peek() == "_"):
            while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
                text += self._advance()
            raise LexicalError(f"invalid token '{text}'", line, col)
        return Token(NUM, text, line, col)

    # ---- main entry point ---------------------------------------------
    def next_token(self):
        self._skip_whitespace()
        line, col = self.line, self.col
        ch = self._peek()

        if ch == "":
            return Token(EOF, "", line, col)
        if ch.isalpha() or ch == "_":
            return self._identifier_or_keyword(line, col)
        if ch.isdigit():
            return self._number(line, col)
        if ch in SYMBOLS:
            self._advance()
            return Token(SYMBOLS[ch], ch, line, col)

        raise LexicalError(f"unexpected character '{ch}'", line, col)

    def tokenize(self):
        """Return the full list of tokens, ending with an EOF token."""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == EOF:
                return tokens


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "-f":
        if len(args) < 2:
            print("Error: -f needs a file name")
            return 1
        with open(args[1], encoding="utf-8") as f:
            source = f.read()
    else:
        source = " ".join(args)

    try:
        for tok in Lexer(source).tokenize():
            print(tok)
    except LexicalError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
