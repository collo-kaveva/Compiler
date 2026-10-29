import unittest
from lexical_analyser import Lexer, LexicalError


def types(src):
    return [t.type for t in Lexer(src).tokenize()]


class ValidInput(unittest.TestCase):
    def test_simple_declaration(self):
        self.assertEqual(types("int x;"), ["INT", "ID", "SEMI", "EOF"])

    def test_float_declaration(self):
        self.assertEqual(types("float total;"), ["FLOAT", "ID", "SEMI", "EOF"])

    def test_init_with_number(self):
        self.assertEqual(types("int count = 10;"),
                         ["INT", "ID", "ASSIGN", "NUM", "SEMI", "EOF"])

    def test_init_with_expression(self):
        self.assertEqual(types("int total = x + 10;"),
                         ["INT", "ID", "ASSIGN", "ID", "PLUS", "NUM", "SEMI", "EOF"])

    def test_no_spaces(self):
        self.assertEqual(types("int a=1+2;"),
                         ["INT", "ID", "ASSIGN", "NUM", "PLUS", "NUM", "SEMI", "EOF"])

    def test_keyword_vs_identifier(self):
        self.assertEqual(types("integer"), ["ID", "EOF"])
        self.assertEqual(types("int"), ["INT", "EOF"])

    def test_lexemes(self):
        toks = Lexer("int count_1 = 42;").tokenize()
        self.assertEqual([t.lexeme for t in toks][:-1],
                         ["int", "count_1", "=", "42", ";"])

    def test_line_and_column(self):
        toks = Lexer("int x;\nfloat y;").tokenize()
        float_tok = toks[3]
        self.assertEqual((float_tok.line, float_tok.column), (2, 1))

    def test_empty_input(self):
        self.assertEqual(types(""), ["EOF"])


class InvalidInput(unittest.TestCase):
    def test_illegal_character(self):
        with self.assertRaises(LexicalError):
            Lexer("int x @ 5;").tokenize()

    def test_multiplication_not_in_language(self):
        with self.assertRaises(LexicalError):
            Lexer("int x = 2 * 3;").tokenize()

    def test_number_followed_by_letters(self):
        with self.assertRaises(LexicalError):
            Lexer("int x = 12abc;").tokenize()

    def test_identifier_cannot_start_with_digit(self):
        with self.assertRaises(LexicalError):
            Lexer("int 1x;").tokenize()


class LexerDoesNotCheckSyntax(unittest.TestCase):
    """The lexer only produces tokens. Rejecting 'int x' is the parser's job."""

    def test_missing_semicolon_still_tokenizes(self):
        self.assertEqual(types("int x"), ["INT", "ID", "EOF"])

    def test_bad_order_still_tokenizes(self):
        self.assertEqual(types("= x;"), ["ASSIGN", "ID", "SEMI", "EOF"])


if __name__ == "__main__":
    unittest.main()
