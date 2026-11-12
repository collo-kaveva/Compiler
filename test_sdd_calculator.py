import unittest
from lexical_analyser import LexicalError
from sdd_calculator import Parser, tokenize
from syntax_analyser import ParseError


def evaluate(expression):
    """Annotated parse tree of the expression."""
    return Parser(tokenize(expression)).parse()


class Evaluate(unittest.TestCase):
    def test_annotated_tree_values(self):
        tree = evaluate("(3+4)*(5+6)")
        self.assertEqual(tree.val, 77)
        product = tree.children[0].children[0]
        self.assertEqual([c.label() for c in product.children],
                         ["T.val = 7", "*", "F.val = 11"])

    def test_multiplication_before_addition(self):
        self.assertEqual(evaluate("3+4*5").val, 23)
        self.assertEqual(evaluate("(3+4)*5").val, 35)

    def test_numbers_with_several_digits(self):
        self.assertEqual(evaluate("12 * 3").val, 36)

    def test_addition_groups_to_the_left(self):
        e = evaluate("1+2+3").children[0]
        self.assertEqual([c.label() for c in e.children], ["E.val = 3", "+", "T.val = 3"])

    def test_tree_lines_with_semantic_rules(self):
        self.assertEqual(evaluate("2*3").lines(), [
            ("L.val = 6", "L.val = E.val"),
            ("├── E.val = 6", "E.val = T.val"),
            ("│   └── T.val = 6", "T.val = T1.val * F.val"),
            ("│       ├── T.val = 2", "T.val = F.val"),
            ("│       │   └── F.val = 2", "F.val = digit.lexval"),
            ("│       │       └── digit.lexval = 2", ""),
            ("│       ├── *", ""),
            ("│       └── F.val = 3", "F.val = digit.lexval"),
            ("│           └── digit.lexval = 3", ""),
            ("└── n", ""),
        ])


class NotValid(unittest.TestCase):
    def assertNotValid(self, expression, rule, message):
        with self.assertRaises(ParseError) as ctx:
            evaluate(expression)
        self.assertEqual(ctx.exception.rule, rule)
        self.assertIn(message, str(ctx.exception))

    def test_missing_close_paren(self):
        self.assertNotValid("(3+4", "F → ( E )",
                            "expected '+', '*' or ')', found end of line")

    def test_missing_operand(self):
        self.assertNotValid("3+", "F → ( E ) | digit",
                            "expected digit or '(', found end of line")

    def test_missing_operator(self):
        self.assertNotValid("3 4", "L → E n",
                            "expected '+', '*' or end of line, found '4'")

    def test_invalid_character(self):
        with self.assertRaises(LexicalError):
            evaluate("3-4")


if __name__ == "__main__":
    unittest.main()
