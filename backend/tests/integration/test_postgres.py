"""Real PostgreSQL tests. CI supplies an ephemeral service; local runs may skip."""
import os
import unittest
import uuid
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from fastapi.testclient import TestClient
from backend.main import create_app


@unittest.skipUnless(os.environ.get('TEST_POSTGRES_URL'), 'Disposable PostgreSQL test URL not configured')
class PostgresTests(unittest.TestCase):
    def setUp(self):
        self.base = os.environ['TEST_POSTGRES_URL']
        self.schema = 'test_' + uuid.uuid4().hex
        with psycopg.connect(self.base, autocommit=True) as connection:
            connection.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.addCleanup(self.cleanup_schema)
        self.url = make_conninfo(self.base, options='-c search_path=' + self.schema)

    def cleanup_schema(self):
        with psycopg.connect(self.base, autocommit=True) as connection:
            connection.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def test_full_workflow_and_restart(self):
        with TestClient(create_app(database_url=self.url)) as client:
            self.assertEqual(client.get('/api/replies').json(), {'items': [], 'total': 0})
            draft = client.post('/api/drafts', json={'question': 'What is your return policy?'}).json()
            response = client.post('/api/replies', json={'question': draft['question'], 'reply': draft['draft'], 'faq_id': draft['source']['id']})
            self.assertEqual(response.status_code, 201)
            saved = response.json()
        with TestClient(create_app(database_url=self.url)) as client:
            self.assertEqual(client.get('/api/replies').json()['items'], [saved])
            self.assertEqual(client.get('/api/replies/'+str(saved['id'])).json(), saved)
            self.assertEqual(client.get('/api/replies/'+str(2**63)).status_code, 404)
            self.assertEqual(client.get('/api/replies?offset='+str(2**63)).json(), {'items': [], 'total': 1})

    def test_manual_reply_pagination_and_sql_text(self):
        with TestClient(create_app(database_url=self.url)) as client:
            saved = []
            for index in range(3):
                response = client.post('/api/replies', json={'question': 'Synthetic question '+str(index), 'reply': "'); DROP TABLE replies; --", 'faq_id': None})
                self.assertEqual(response.status_code, 201)
                saved.append(response.json())
            page = client.get('/api/replies?limit=1&offset=1').json()
            self.assertEqual(page, {'items': [saved[1]], 'total': 3})
            self.assertEqual(client.get('/api/replies/99999').status_code, 404)
