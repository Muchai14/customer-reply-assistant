"""Exercise request boundaries without touching hosted or local user data."""
import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
import yaml

from backend.main import create_app
from backend.request_limits import MAX_BODY_BYTES, RequestBodyLimit


class RequestLimitTests(unittest.TestCase):
    def test_oversized_valid_json_cannot_save_and_matches_contract(self):
        with TemporaryDirectory() as directory, TestClient(create_app(Path(directory) / "test.db")) as client:
            payload = json.dumps({"question": "Return policy?", "reply": "Demo only", "faq_id": None})
            for path in ("/api/replies", "/api/drafts"):
                response = client.post(path, content=payload + " " * MAX_BODY_BYTES,
                                       headers={"Content-Type": "application/json"})
                self.assertEqual(response.status_code, 413)
                contract = yaml.safe_load((Path(__file__).resolve().parents[3] / "openapi.yaml").read_text())
                response_name = contract["paths"][path]["post"]["responses"]["413"]["$ref"].split("/")[-1]
                schema = contract["components"]["responses"][response_name]["content"]["application/json"]["schema"]
                Draft202012Validator(schema).validate(response.json())
            self.assertEqual(client.get("/api/replies").json()["total"], 0)

    def test_largest_allowed_fields_with_escaped_unicode_still_save(self):
        with TemporaryDirectory() as directory, TestClient(create_app(Path(directory) / "test.db")) as client:
            payload = {"question": "😀" * 1000, "reply": "😀" * 5000, "faq_id": None}
            response = client.post("/api/replies", content=json.dumps(payload, ensure_ascii=True),
                                   headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 201, response.text)
            self.assertEqual(response.json()["reply"], payload["reply"])

    def test_chunked_actual_size_is_enforced_without_trusting_headers(self):
        async def scenario(headers):
            messages = iter([
                {"type": "http.request", "body": b"x" * MAX_BODY_BYTES, "more_body": True},
                {"type": "http.request", "body": b"x", "more_body": True},
            ])
            sent = []
            async def receive():
                return next(messages)
            async def send(message):
                sent.append(message)
            async def downstream(scope, receive, send):
                self.fail("Oversized data reached the parser")
            await RequestBodyLimit(downstream)({"type": "http", "path": "/api/replies", "headers": headers}, receive, send)
            self.assertEqual(sent[0]["status"], 413)
        for headers in ([], [(b"content-length", b"1")]):
            asyncio.run(scenario(headers))

    def test_exact_limit_is_delivered_and_disconnect_does_not_call_app(self):
        async def scenario(disconnect):
            messages = iter([{"type": "http.disconnect"}] if disconnect else [
                {"type": "http.request", "body": b"a" * (MAX_BODY_BYTES - 1), "more_body": True},
                {"type": "http.request", "body": b"b", "more_body": False},
            ])
            calls = []
            async def receive():
                return next(messages)
            async def send(message):
                self.fail("Unexpected middleware response")
            async def downstream(scope, receive, send):
                calls.append(await receive())
            await RequestBodyLimit(downstream)({"type": "http", "path": "/api/replies"}, receive, send)
            self.assertEqual(len(calls), 0 if disconnect else 1)
            if calls:
                self.assertEqual(calls[0]["body"], b"a" * (MAX_BODY_BYTES - 1) + b"b")
        asyncio.run(scenario(False))
        asyncio.run(scenario(True))
