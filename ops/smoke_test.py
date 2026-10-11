"""Smoke test for an isolated CI application; creates one synthetic saved reply.

Run only against a disposable test instance, not a production service.
Usage: python3 ops/smoke_test.py [base_url]
"""
import json
import sys
from urllib.request import Request, urlopen


def check(base_url):
    def request(path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(base_url.rstrip('/') + path, data=data,
                      headers={'Content-Type': 'application/json'} if data else {})
        with urlopen(req, timeout=10) as response:
            return response.status, response.read()

    status, page = request('/')
    assert status == 200 and b'Customer Reply Assistant' in page
    for asset in ['styles.css', 'app.js', 'api.js', 'state.js']:
        assert request('/assets/' + asset)[0] == 200
    _, body = request('/api/drafts', {'question': 'What is your return policy?'})
    draft = json.loads(body)
    assert draft['matched'] and draft['source']['id'] == 'faq-101'
    status, body = request('/api/replies', {
        'question': draft['question'], 'reply': draft['draft'], 'faq_id': draft['source']['id'],
    })
    assert status == 201
    saved = json.loads(body)
    assert json.loads(request('/api/replies/' + str(saved['id']))[1]) == saved
    history = json.loads(request('/api/replies?limit=100')[1])
    assert any(item['id'] == saved['id'] for item in history['items'])
    print('PASS: webpage, static assets, draft generation, saving, history, and detail.')


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000')
