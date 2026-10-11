"""Small SQLite repository; connections are closed after each operation."""

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Optional


class ReplyStore:
    def __init__(self, path: Path):
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS replies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL CHECK(length(question) BETWEEN 1 AND 1000),
                        reply TEXT NOT NULL CHECK(length(reply) BETWEEN 1 AND 5000),
                        faq_id TEXT,
                        created_at TEXT NOT NULL
                    )
                """)

    def save(self, question: str, reply: str, faq_id: Optional[str]) -> dict:
        created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            with connection:
                cursor = connection.execute(
                    "INSERT INTO replies (question, reply, faq_id, created_at) VALUES (?, ?, ?, ?)",
                    (question, reply, faq_id, created_at),
                )
                row = connection.execute("SELECT * FROM replies WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return dict(row)

    def list_replies(self, limit: int, offset: int) -> dict:
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            # Keep the count and page in the same read snapshot.
            with connection:
                connection.execute("BEGIN")
                total = connection.execute("SELECT COUNT(*) FROM replies").fetchone()[0]
                if offset >= total:
                    return {"items": [], "total": total}
                rows = connection.execute(
                    "SELECT * FROM replies ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
            return {"items": [dict(row) for row in rows], "total": total}

    def get_reply(self, reply_id: int) -> Optional[dict]:
        # SQLite integer primary keys cannot exceed signed 64-bit range.
        if reply_id > 2**63 - 1:
            return None
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute("SELECT * FROM replies WHERE id = ?", (reply_id,)).fetchone()
            return dict(row) if row is not None else None
