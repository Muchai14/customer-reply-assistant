"""PostgreSQL repository for persistent hosted storage."""
from datetime import datetime, timezone
import psycopg
from psycopg.rows import dict_row


class PostgresReplyStore:
    def __init__(self, url):
        self.url = url

    def connect(self):
        return psycopg.connect(self.url, row_factory=dict_row, connect_timeout=15)

    def initialize(self):
        with self.connect() as connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS replies (
                id BIGSERIAL PRIMARY KEY,
                question TEXT NOT NULL CHECK(char_length(question) BETWEEN 1 AND 1000),
                reply TEXT NOT NULL CHECK(char_length(reply) BETWEEN 1 AND 5000),
                faq_id TEXT,
                created_at TEXT NOT NULL
            )''')

    def save(self, question, reply, faq_id):
        timestamp = datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')
        with self.connect() as connection:
            return connection.execute(
                'INSERT INTO replies (question, reply, faq_id, created_at) VALUES (%s, %s, %s, %s) RETURNING *',
                (question, reply, faq_id, timestamp),
            ).fetchone()

    def list_replies(self, limit, offset):
        with self.connect() as connection:
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            total = connection.execute('SELECT COUNT(*) AS total FROM replies').fetchone()['total']
            if offset >= total:
                return {'items': [], 'total': total}
            items = connection.execute('SELECT * FROM replies ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s', (limit, offset)).fetchall()
            return {'items': items, 'total': total}

    def get_reply(self, reply_id):
        if reply_id > 2**63 - 1:
            return None
        with self.connect() as connection:
            return connection.execute('SELECT * FROM replies WHERE id = %s', (reply_id,)).fetchone()
