"""History contract tests using real temporary SQLite storage."""

from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
import yaml

from backend.main import create_app


ROOT = Path(__file__).resolve().parents[3]


class HistoryApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "openapi.yaml").read_text())

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "history.db"
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def assert_contract(self, response, status, name):
        self.assertEqual(response.status_code, status, response.text)
        schema = {"$ref": "#/components/schemas/" + name, "components": self.contract["components"]}
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(response.json())

    def save(self, count=1):
        records = []
        for index in range(count):
            response = self.client.post("/api/replies", json={
                "question": "Customer question " + str(index),
                "reply": "Reviewed reply " + str(index), "faq_id": None,
            })
            self.assert_contract(response, 201, "SavedReply")
            records.append(response.json())
        return records

    def test_empty_history(self):
        response = self.client.get("/api/replies")
        self.assert_contract(response, 200, "ReplyList")
        self.assertEqual(response.json(), {"items": [], "total": 0})

    def test_list_and_detail_return_saved_content(self):
        records = self.save(3)
        response = self.client.get("/api/replies")
        self.assert_contract(response, 200, "ReplyList")
        self.assertEqual(response.json(), {"items": list(reversed(records)), "total": 3})
        for record in records:
            detail = self.client.get('/api/replies/' + str(record['id']))
            self.assert_contract(detail, 200, "SavedReply")
            self.assertEqual(detail.json(), record)

    def test_pagination_and_default_page_size(self):
        records = list(reversed(self.save(23)))
        default_page = self.client.get("/api/replies")
        self.assert_contract(default_page, 200, "ReplyList")
        self.assertEqual(default_page.json(), {"items": records[:20], "total": 23})
        page = self.client.get("/api/replies?limit=2&offset=2")
        self.assert_contract(page, 200, "ReplyList")
        self.assertEqual(page.json(), {"items": records[2:4], "total": 23})
        beyond = self.client.get("/api/replies?offset=23")
        self.assert_contract(beyond, 200, "ReplyList")
        self.assertEqual(beyond.json(), {"items": [], "total": 23})
        maximum = self.client.get("/api/replies?limit=100")
        self.assert_contract(maximum, 200, "ReplyList")
        self.assertEqual(maximum.json()["items"], records)

    def test_timestamp_order_and_id_tie_break(self):
        records = self.save(3)
        # Force timestamps to verify ordering independently of insertion timing.
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                for index, record in enumerate(records):
                    timestamp = "2026-10-10T12:00:00Z" if index < 2 else "2026-10-09T12:00:00Z"
                    connection.execute("UPDATE replies SET created_at = ? WHERE id = ?", (timestamp, record["id"]))
        response = self.client.get("/api/replies")
        self.assert_contract(response, 200, "ReplyList")
        self.assertEqual([r["id"] for r in response.json()["items"]], [records[1]["id"], records[0]["id"], records[2]["id"]])

    def test_large_integers_do_not_cause_server_errors(self):
        self.save()
        huge = str(2**63)
        detail = self.client.get("/api/replies/" + huge)
        self.assert_contract(detail, 404, "NotFoundError")
        page = self.client.get("/api/replies?offset=" + huge)
        self.assert_contract(page, 200, "ReplyList")
        self.assertEqual(page.json(), {"items": [], "total": 1})

    def test_missing_record(self):
        response = self.client.get("/api/replies/999")
        self.assert_contract(response, 404, "NotFoundError")
        self.assertEqual(response.json(), {"detail": "Reply not found."})

    def test_invalid_query_and_path_parameters(self):
        paths = ["?limit=0", "?limit=101", "?limit=abc", "?limit=1.5", "?offset=-1", "?offset=abc",
                 "/0", "/-1", "/abc", "/1.5"]
        for suffix in paths:
            with self.subTest(suffix=suffix):
                self.assert_contract(self.client.get("/api/replies" + suffix), 422, "ValidationError")

    def test_history_available_after_restart(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "restart.db"
            with TestClient(create_app(path)) as initial:
                record = initial.post("/api/replies", json={"question": "refund", "reply": "Reviewed answer", "faq_id": "faq-103"}).json()
            with TestClient(create_app(path)) as restarted:
                history = restarted.get("/api/replies")
                self.assert_contract(history, 200, "ReplyList")
                self.assertEqual(history.json(), {"items": [record], "total": 1})
                detail = restarted.get('/api/replies/' + str(record['id']))
                self.assert_contract(detail, 200, "SavedReply")
                self.assertEqual(detail.json(), record)

    def test_all_contract_operations_are_exposed(self):
        actual = self.client.get("/openapi.json").json()["paths"]
        for path, methods in self.contract["paths"].items():
            for method, operation in methods.items():
                self.assertEqual(actual[path][method]["operationId"], operation["operationId"])


if __name__ == "__main__":
    unittest.main()
