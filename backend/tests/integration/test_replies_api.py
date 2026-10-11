"""Verify saving through HTTP using real, isolated SQLite databases."""

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
import yaml

from backend.main import create_app


ROOT = Path(__file__).resolve().parents[3]


class ReplyApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "openapi.yaml").read_text())

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "nested" / "test.db"
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.payload = {"question": "What is the return policy?", "reply": "Please check the fictional return policy.", "faq_id": "faq-101"}

    def assert_contract(self, response, status):
        self.assertEqual(response.status_code, status, response.text)
        name = "SavedReply" if status == 201 else "ValidationError"
        schema = {"$ref": "#/components/schemas/" + name, "components": self.contract["components"]}
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(response.json())

    def records(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            return [dict(row) for row in connection.execute("SELECT * FROM replies ORDER BY id")]

    def test_generate_edit_and_save(self):
        draft = self.client.post("/api/drafts", json={"question": "What is your return policy?"}).json()
        self.assertEqual(self.records(), [])
        payload = {"question": draft["question"], "reply": draft["draft"] + " Thank you for checking.", "faq_id": draft["source"]["id"]}
        before = datetime.now(timezone.utc)
        saved = self.client.post("/api/replies", json=payload)
        after = datetime.now(timezone.utc)
        self.assert_contract(saved, 201)
        self.assertEqual(saved.json()["reply"], payload["reply"])
        self.assertEqual(self.records(), [saved.json()])
        timestamp = datetime.fromisoformat(saved.json()["created_at"].replace("Z", "+00:00"))
        self.assertLessEqual(before, timestamp)
        self.assertLessEqual(timestamp, after)

    def test_manual_reply_without_source(self):
        self.payload["faq_id"] = None
        response = self.client.post("/api/replies", json=self.payload)
        self.assert_contract(response, 201)
        self.assertIsNone(self.records()[0]["faq_id"])

    def test_input_is_trimmed_and_maximum_lengths_are_accepted(self):
        payload = {"question": "  " + "q" * 1000 + "\n", "reply": "  " + "r" * 5000 + "\n", "faq_id": None}
        response = self.client.post("/api/replies", json=payload)
        self.assert_contract(response, 201)
        self.assertEqual(len(response.json()["question"]), 1000)
        self.assertEqual(len(response.json()["reply"]), 5000)

    def test_invalid_payloads_do_not_insert_records(self):
        variants = [{}, [], {"question": "x", "reply": "y"}]
        for field, values in {
            "question": ["", " \n", "q" * 1001, None, 1],
            "reply": ["", " \n", "r" * 5001, None, 1],
            "faq_id": ["faq-999", "unknown", "", 1, True],
        }.items():
            variants.extend({**self.payload, field: value} for value in values)
        variants.extend([{**self.payload, "id": 123}, {**self.payload, "created_at": "2020-01-01T00:00:00Z"}])
        for payload in variants:
            with self.subTest(payload=repr(payload)[:100]):
                self.assert_contract(self.client.post("/api/replies", json=payload), 422)
        self.assertEqual(self.records(), [])

    def test_missing_and_malformed_bodies(self):
        self.assert_contract(self.client.post("/api/replies"), 422)
        self.assert_contract(self.client.post("/api/replies", content='{"question":', headers={"Content-Type": "application/json"}), 422)
        self.assertEqual(self.records(), [])

    def test_sql_like_text_is_stored_as_plain_text(self):
        self.payload["reply"] = "Customer said: '); DROP TABLE replies; --"
        first = self.client.post("/api/replies", json=self.payload)
        second = self.client.post("/api/replies", json=self.payload)
        self.assert_contract(first, 201)
        self.assert_contract(second, 201)
        self.assertNotEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(self.records()[0]["reply"], self.payload["reply"])
        self.assertEqual(len(self.records()), 2)

    def test_records_survive_application_restart(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "restart.db"
            with TestClient(create_app(path)) as first_client:
                saved = first_client.post("/api/replies", json=self.payload)
                self.assert_contract(saved, 201)
            with TestClient(create_app(path)) as restarted_client:
                with closing(sqlite3.connect(path)) as connection:
                    connection.row_factory = sqlite3.Row
                    rows = [dict(row) for row in connection.execute("SELECT * FROM replies")]
                self.assertEqual(rows, [saved.json()])
                second = restarted_client.post("/api/replies", json=self.payload)
                self.assert_contract(second, 201)
                self.assertGreater(second.json()["id"], saved.json()["id"])

    def test_environment_can_select_database_location(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "environment.db"
            with patch.dict("os.environ", {"DB_PATH": str(path)}):
                with TestClient(create_app()) as client:
                    self.assert_contract(client.post("/api/replies", json=self.payload), 201)
            with closing(sqlite3.connect(path)) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM replies").fetchone()[0], 1)
            self.assertEqual(self.records(), [])


if __name__ == "__main__":
    unittest.main()
