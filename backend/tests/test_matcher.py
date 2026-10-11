import copy
import json
from pathlib import Path
import unittest

from backend.matcher import load_faqs, match_faq


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faqs = load_faqs()
        cls.ranking_faqs = [
            {"id": "faq-101", "keywords": ["return policy"]},
            {"id": "faq-103", "keywords": ["refund"]},
            {"id": "faq-104", "keywords": ["exchange"]},
        ]

    def assert_match(self, question, expected_id, faqs=None):
        result = match_faq(question, self.faqs if faqs is None else faqs)
        self.assertEqual(result["id"] if result else None, expected_id)

    def test_sample_questions(self):
        path = Path(__file__).parent / "fixtures" / "faq-cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assert_match(case["question"], case["expected_faq_id"])

    def test_case_spacing_and_punctuation(self):
        for question in ["  RETURN    POLICY?  ", "return-policy", "return\npolicy", "ＲＥＴＵＲＮ ＰＯＬＩＣＹ"]:
            with self.subTest(question=question):
                self.assert_match(question, "faq-101")

    def test_underscored_field(self):
        self.assert_match("Explain return_policy", "faq-101")

    def test_substrings_do_not_match(self):
        self.assert_match("My account was recovered; please reinstall the app.", None)

    def test_phrase_must_be_contiguous(self):
        self.assert_match("What is the return eligibility policy?", None)

    def test_more_specific_phrase_wins(self):
        self.assert_match("refund and return policy", "faq-101", self.ranking_faqs)

    def test_tie_is_independent_of_file_order(self):
        self.assert_match("refund and exchange", "faq-103", list(reversed(self.ranking_faqs)))

    def test_repeating_a_keyword_does_not_boost_it(self):
        self.assert_match("refund refund refund return policy", "faq-101", self.ranking_faqs)

    def test_empty_knowledge_base(self):
        self.assert_match("What is the return policy?", None, [])

    def test_punctuation_only_has_no_match(self):
        self.assert_match("?!...", None)

    def test_invalid_questions(self):
        for question in ["", " \n\t", "x" * 1001, None, 42]:
            with self.subTest(question_type=type(question).__name__, length=len(question) if isinstance(question, str) else None):
                with self.assertRaises(ValueError):
                    match_faq(question, self.faqs)

    def test_length_limit_applies_after_trimming(self):
        self.assert_match("  " + "x" * 1000 + "  ", None)

    def test_input_data_is_not_modified(self):
        before = copy.deepcopy(self.faqs)
        match_faq("When will I receive my refund?", self.faqs)
        self.assertEqual(self.faqs, before)


if __name__ == "__main__":
    unittest.main()
