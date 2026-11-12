import unittest
from lexical_analyser import Lexer
from syntax_analyser import ParseError, Parser, leftmost_derivation

DECL = "<decl> → <type> id <init> ;"


def derive(src):
    """(sentential form, production used) for each step of the derivation."""
    return leftmost_derivation(Parser(Lexer(src).tokenize()).parse())


class Valid(unittest.TestCase):
    def test_leftmost_derivation(self):
        forms = [form for form, _ in derive("int total = x + 10;")]
        self.assertEqual(forms, [
            "<program>",
            "<decl>",
            "<type> id <init> ;",
            "int id <init> ;",
            "int id = <expr> ;",
            "int id = <expr> + <term> ;",
            "int id = <term> + <term> ;",
            "int id = id + <term> ;",
            "int id = id + number ;",
        ])

    def test_empty_init_uses_epsilon(self):
        steps = derive("int x;")
        self.assertEqual(steps[-1], ("int id ;", "<init> → ε"))

    def test_productions_used(self):
        productions = [p for _, p in derive("float y = 1;")][1:]
        self.assertEqual(productions, [
            "<program> → <decl>",
            "<decl> → <type> id <init> ;",
            "<type> → float",
            "<init> → = <expr>",
            "<expr> → <term>",
            "<term> → number",
        ])

    def test_several_declarations(self):
        forms = [form for form, _ in derive("int x;\nfloat y = a + b + 1;")]
        self.assertEqual(forms[1], "<decl> <program>")
        self.assertEqual(forms[-1], "int id ; float id = id + id + number ;")


class NotValid(unittest.TestCase):
    """The first five match 'Rejected Inputs' in Context Free Grammar.md."""

    def assertNotValid(self, src, rule, message):
        with self.assertRaises(ParseError) as ctx:
            derive(src)
        self.assertEqual(ctx.exception.rule, rule)
        self.assertIn(message, str(ctx.exception))

    def test_must_start_with_type(self):
        self.assertNotValid("= x;", DECL, "expected 'int' or 'float', found '='")

    def test_id_required_after_type(self):
        self.assertNotValid("int = 10;", DECL, "expected id, found '='")

    def test_semicolon_is_mandatory(self):
        self.assertNotValid("int x", DECL, "expected '=' or ';', found end of input")

    def test_init_needs_expression(self):
        self.assertNotValid("int x =;", "<init> → = <expr>",
                            "expected id or number, found ';'")

    def test_plus_only_after_assign(self):
        self.assertNotValid("int x + 10;", DECL, "expected '=' or ';', found '+'")

    def test_plus_needs_term(self):
        self.assertNotValid("int x = y + ;", "<expr> → <expr> + <term>",
                            "expected id or number, found ';'")

    def test_terms_need_plus_between(self):
        self.assertNotValid("int x = 10 5;", DECL, "expected '+' or ';', found '5'")

    def test_empty_input(self):
        self.assertNotValid("", DECL, "expected 'int' or 'float', found end of input")

    def test_error_position(self):
        with self.assertRaises(ParseError) as ctx:
            derive("int x;\nfloat y = ;")
        self.assertEqual((ctx.exception.line, ctx.exception.column), (2, 11))


if __name__ == "__main__":
    unittest.main()
