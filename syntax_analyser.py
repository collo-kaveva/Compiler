"""
Syntax Analyser: proves whether the input is VALID or NOT VALID.

Grammar (see "Context Free Grammar.md"):
    <program> → <decl> <program> | <decl>
    <decl>    → <type> id <init> ;
    <type>    → int | float
    <init>    → = <expr> | ε
    <expr>    → <expr> + <term> | <term>
    <term>    → id | number

VALID input is proven with a leftmost derivation from <program>.
NOT VALID input gets the error position and the rule it breaks.

Usage:
    uv run syntax_analyser.py "int total = x + 10;"
    uv run syntax_analyser.py -f sample.txt
"""

import sys
from dataclasses import dataclass, field

from lexical_analyser import (
    ASSIGN, EOF, FLOAT, ID, INT, NUMBER, PLUS, SEMI, Lexer, LexicalError, read_source,
)

# Grammar terminal that each token type stands for
TERMINALS = {
    INT: "int", FLOAT: "float", ID: "id", NUMBER: "number",
    ASSIGN: "=", PLUS: "+", SEMI: ";",
}

DECL_RULE = "<decl> → <type> id <init> ;"
INIT_RULE = "<init> → = <expr>"
PLUS_RULE = "<expr> → <expr> + <term>"


class ParseError(Exception):
    """Raised when the tokens break a grammar rule."""

    def __init__(self, message, rule, line, column):
        super().__init__(f"Syntax error at line {line}, column {column}: {message}")
        self.rule = rule
        self.line = line
        self.column = column


@dataclass
class Node:
    """A non-terminal and the symbols it was replaced by (Nodes or terminals)."""

    symbol: str
    children: list = field(default_factory=list)

    def __str__(self):
        return self.symbol

    def production(self):
        return f"{self.symbol} → {' '.join(map(str, self.children)) or 'ε'}"


def leftmost_derivation(tree):
    """Expand the leftmost non-terminal until only terminals remain."""
    form = [tree]
    steps = [(str(tree), "")]
    while any(isinstance(s, Node) for s in form):
        i = next(k for k, s in enumerate(form) if isinstance(s, Node))
        node = form[i]
        form[i:i + 1] = node.children
        steps.append((" ".join(map(str, form)), node.production()))
    return steps


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
        return TERMINALS[tok.type]

    def _expect(self, token_type, expected, rule):
        if self._peek() != token_type:
            raise self._error(expected, rule)
        return self._take()

    def _error(self, expected, rule):
        tok = self.tokens[self.pos]
        found = "end of input" if tok.type == EOF else f"'{tok.lexeme}'"
        message = f"expected {expected}, found {found}"
        return ParseError(message, rule, tok.line, tok.column)

    # ---- one method per non-terminal -----------------------------------
    def parse(self):
        """Parse all tokens as a <program> and return its parse tree."""
        return self._program()

    def _program(self):
        decl = self._decl()
        if self._peek() == EOF:
            return Node("<program>", [decl])
        return Node("<program>", [decl, self._program()])

    def _decl(self):
        type_ = self._type()
        name = self._expect(ID, "id", DECL_RULE)
        init = self._init()
        end = "'+' or ';'" if init.children else "'=' or ';'"
        semi = self._expect(SEMI, end, DECL_RULE)
        return Node("<decl>", [type_, name, init, semi])

    def _type(self):
        if self._peek() not in (INT, FLOAT):
            raise self._error("'int' or 'float'", DECL_RULE)
        return Node("<type>", [self._take()])

    def _init(self):
        if self._peek() == ASSIGN:
            return Node("<init>", [self._take(), self._expr()])
        return Node("<init>")

    def _expr(self):
        # Left recursion as a loop: each '+' wraps the expression built so far.
        expr = Node("<expr>", [self._term(INIT_RULE)])
        while self._peek() == PLUS:
            expr = Node("<expr>", [expr, self._take(), self._term(PLUS_RULE)])
        return expr

    def _term(self, rule):
        if self._peek() not in (ID, NUMBER):
            raise self._error("id or number", rule)
        return Node("<term>", [self._take()])


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    source = read_source(args)

    try:
        tokens = Lexer(source).tokenize()
        tree = Parser(tokens).parse()
    except LexicalError as e:
        print(f"NOT VALID: {e}")
        return 1
    except ParseError as e:
        print(f"NOT VALID: {e}")
        print(f"Rule violated: {e.rule}")
        return 1

    steps = leftmost_derivation(tree)
    width = max(len(form) for form, _ in steps) + 4
    print(f"  {'Leftmost derivation':<{width}}Production used")
    for i, (form, production) in enumerate(steps):
        arrow = "⇒ " if i else "  "
        print(f"{arrow}{form:<{width}}{production}".rstrip())
    print(f"\nVALID: {' '.join(tok.lexeme for tok in tokens[:-1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
