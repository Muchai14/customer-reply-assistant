"""Reproduce and diagnose a storage startup fault in disposable directories only."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from backend.main import create_app


def diagnose():
    evidence = {'scope': 'Temporary local test databases only; no user records accessed.'}
    with TemporaryDirectory() as directory:
        root = Path(directory)
        invalid_parent = root / 'not-a-directory'
        invalid_parent.write_text('synthetic obstruction')
        try:
            with TestClient(create_app(invalid_parent / 'replies.db')):
                pass
        except OSError as error:
            evidence['injected_fault'] = 'DB_PATH parent is a regular file'
            evidence['observed_startup_error'] = type(error).__name__
        else:
            raise AssertionError('Expected storage initialization to fail')
        valid_path = root / 'data' / 'replies.db'
        with TestClient(create_app(valid_path)) as client:
            saved = client.post('/api/replies', json={
                'question': 'What is your return policy?', 'reply': 'Synthetic reviewed reply.', 'faq_id': 'faq-101',
            })
            if saved.status_code != 201:
                raise AssertionError('Saving after recovery failed')
            record = saved.json()
        with TestClient(create_app(valid_path)) as client:
            history = client.get('/api/replies')
            if history.status_code != 200 or history.json()['items'] != [record]:
                raise AssertionError('Persistence after restart failed')
        evidence['recovery'] = 'Use a writable directory for DB_PATH; startup and save succeeded.'
        evidence['save_status'] = 201
        evidence['history_after_restart'] = {'status': 200, 'records': 1, 'saved_content_preserved': True}
    return evidence


if __name__ == '__main__':
    print(json.dumps(diagnose(), indent=2))
