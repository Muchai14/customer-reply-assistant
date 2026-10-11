"""Exercise the real request validation, matcher, and response serialization."""

import copy
import json
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
import yaml

from backend.main import create_app


ROOT = Path(__file__).resolve().parents[3]


class DraftApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "openapi.yaml").read_text(encoding="utf-8"))
        cls.cases = json.loads((ROOT / "backend/tests/fixtures/faq-cases.json").read_text())["cases"]

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.app = create_app(Path(temporary.name) / "test.db")
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def assert_contract(self, response, status):
        self.assertEqual(response.status_code, status, response.text)
        schema = {"$ref": "#/components/schemas/" + ("DraftResult" if status == 200 else "ValidationError"),
                  "components": self.contract["components"]}
        Draft202012Validator(schema).validate(response.json())

    def test_all_fifteen_sample_questions(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                response = self.client.post("/api/drafts", json={"question": case["question"]})
                self.assert_contract(response, 200)
                body = response.json()
                self.assertEqual(body["question"], case["question"])
                self.assertEqual(body["matched"], case["expected_faq_id"] is not None)
                if body["matched"]:
                    self.assertEqual(body["source"]["id"], case["expected_faq_id"])
                    self.assertEqual(body["draft"], "Hello, " + body["source"]["answer"])
                else:
                    self.assertEqual(body["draft"], "")
                    self.assertIsNone(body["source"])
                    self.assertIn("No matching FAQ", body["message"])

    def test_question_is_trimmed(self):
        response = self.client.post("/api/drafts", json={"question": "  return policy\n"})
        self.assert_contract(response, 200)
        self.assertEqual(response.json()["question"], "return policy")

    def test_input_limits_after_trimming(self):
        self.assert_contract(self.client.post("/api/drafts", json={"question": "  " + "x" * 1000 + "  "}), 200)
        self.assert_contract(self.client.post("/api/drafts", json={"question": "x" * 1001}), 422)

    def test_invalid_payloads(self):
        for payload in [{}, {"question": ""}, {"question": " \n\t"},
                        {"question": None}, {"question": 42}, {"question": True},
                        {"question": ["refund"]}, {"question": "refund", "extra": "forbidden"}, []]:
            with self.subTest(payload=payload):
                self.assert_contract(self.client.post("/api/drafts", json=payload), 422)

    def test_missing_body(self):
        self.assert_contract(self.client.post("/api/drafts"), 422)

    def test_malformed_json(self):
        response = self.client.post("/api/drafts", content='{"question":', headers={"Content-Type": "application/json"})
        self.assert_contract(response, 422)

    def test_repeated_requests_are_stable_and_do_not_change_faqs(self):
        before = copy.deepcopy(self.app.state.faqs)
        first = self.client.post("/api/drafts", json={"question": "refund"})
        second = self.client.post("/api/drafts", json={"question": "refund"})
        self.assert_contract(first, 200)
        self.assertEqual(first.json(), second.json())
        self.assertEqual(self.app.state.faqs, before)

    def test_docs_are_available(self):
        self.assertEqual(self.client.get("/docs").status_code, 200)


if __name__ == "__main__":
    unittest.main()
