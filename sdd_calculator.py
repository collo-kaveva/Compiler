"""
Syntax-directed calculator: evaluates + and * expressions and prints the
annotated parse tree.

A syntax-directed definition gives each production a semantic rule that
computes the synthesized attribute val:

    Production       Semantic rule
    L → E n          L.val = E.val
    E → E1 + T       E.val = E1.val + T.val
    E → T            E.val = T.val
    T → T1 * F       T.val = T1.val * F.val
    T → F            T.val = F.val
    F → ( E )        F.val = E.val
    F → digit        F.val = digit.lexval

n is the end of the line; digit is a whole number whose lexval is its value.

Usage:
    uv run sdd_calculator.py "(3+4)*(5+6)"
"""

import re
import sys
from dataclasses import dataclass, field

from lexical_analyser import LexicalError, Token
from syntax_analyser import ParseError

LEXEME = re.compile(r"(?P<digit>[0-9]+)|(?P<symbol>\S)")


def tokenize(line):
    """Tokens of one line, ending with the end-of-line token n."""
    tokens = []
    for match in LEXEME.finditer(line):
        text, col = match.group(), match.start() + 1
        if match.lastgroup == "digit":
            tokens.append(Token("digit", text, 1, col))
        elif text in "+*()":
            tokens.append(Token(text, text, 1, col))
        else:
            raise LexicalError(f"unexpected character '{text}'", 1, col)
    tokens.append(Token("n", "", 1, len(line) + 1))
    return tokens


@dataclass
class Node:
    """Parse tree node with its synthesized val and the semantic rule that set it."""

    symbol: str
    val: int | None = None
    rule: str = ""
    children: list = field(default_factory=list)

    def label(self):
        if self.symbol == "digit":
            return f"digit.lexval = {self.val}"
        if self.val is None:
            return self.symbol
        return f"{self.symbol}.val = {self.val}"

    def lines(self, prefix="", indent=""):
        """(tree line, semantic rule) for this node and everything under it."""
        rows = [(prefix + self.label(), self.rule)]
        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            rows += child.lines(indent + ("└── " if last else "├── "),
                                indent + ("    " if last else "│   "))
        return rows


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- helpers -------------------------------------------------------
    def _peek(self):
        return self.tokens[self.pos].type

    def _take(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, symbol, expected, rule):
        if self._peek() != symbol:
            raise self._error(expected, rule)
        return Node(self._take().type)

    def _error(self, expected, rule):
        tok = self.tokens[self.pos]
        found = "end of line" if tok.type == "n" else f"'{tok.lexeme}'"
        message = f"expected {expected}, found {found}"
        return ParseError(message, rule, tok.line, tok.column)

    # ---- one method per non-terminal, each computing its val -----------
    def parse(self):
        """Parse the line and return its annotated parse tree."""
        e = self._expr()
        n = self._expect("n", "'+', '*' or end of line", "L → E n")
        return Node("L", e.val, "L.val = E.val", [e, n])

    def _expr(self):
        # Left recursion as a loop: each '+' wraps the E built so far.
        t = self._term()
        e = Node("E", t.val, "E.val = T.val", [t])
        while self._peek() == "+":
            plus = Node(self._take().type)
            t = self._term()
            e = Node("E", e.val + t.val, "E.val = E1.val + T.val", [e, plus, t])
        return e

    def _term(self):
        f = self._factor()
        t = Node("T", f.val, "T.val = F.val", [f])
        while self._peek() == "*":
            star = Node(self._take().type)
            f = self._factor()
            t = Node("T", t.val * f.val, "T.val = T1.val * F.val", [t, star, f])
        return t

    def _factor(self):
        if self._peek() == "(":
            lparen = Node(self._take().type)
            e = self._expr()
            rparen = self._expect(")", "'+', '*' or ')'", "F → ( E )")
            return Node("F", e.val, "F.val = E.val", [lparen, e, rparen])
        if self._peek() == "digit":
            lexval = int(self._take().lexeme)
            return Node("F", lexval, "F.val = digit.lexval", [Node("digit", lexval)])
        raise self._error("digit or '('", "F → ( E ) | digit")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    line = " ".join(sys.argv[1:])

    try:
        tree = Parser(tokenize(line)).parse()
    except LexicalError as e:
        print(f"NOT VALID: {e}")
        return 1
    except ParseError as e:
        print(f"NOT VALID: {e}")
        print(f"Rule violated: {e.rule}")
        return 1

    rows = tree.lines()
    width = max(len(text) for text, _ in rows) + 4
    print(f"{'Annotated parse tree':<{width}}Semantic rule")
    for text, rule in rows:
        print(f"{text:<{width}}{rule}".rstrip())
    print(f"\n{line} = {tree.val}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
