"""Exercise the extension subprocess and staged-index guardrail with synthetic data."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('guardrail', ROOT / 'agent-hooks/check_staged.py')
guardrail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardrail)


def request(number, method, params=None):
    return {'jsonrpc': '2.0', 'id': number, 'method': method, 'params': params or {}}


INIT = request(1, 'initialize', {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}})
READY = {'jsonrpc': '2.0', 'method': 'notifications/initialized'}


class MCPTests(unittest.TestCase):
    def run_messages(self, messages):
        lines = '\n'.join(json.dumps(x) if not isinstance(x, str) else x for x in messages) + '\n'
        result = subprocess.run([sys.executable, str(ROOT / 'mcp-server/server.py')], input=lines,
                                capture_output=True, text=True, timeout=10, cwd='/tmp')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return [json.loads(line) for line in result.stdout.splitlines()]

    def test_initialization_and_tools(self):
        replies = self.run_messages([INIT, READY, request(2, 'tools/list')])
        self.assertEqual(len(replies), 2)
        self.assertEqual(replies[0]['result']['protocolVersion'], '2025-06-18')
        tools = replies[1]['result']['tools']
        self.assertEqual({tool['name'] for tool in tools}, {'search_faq', 'get_faq'})
        self.assertTrue(all(tool['annotations']['readOnlyHint'] for tool in tools))

    def test_lookup_and_no_match(self):
        replies = self.run_messages([INIT, READY,
            request(2, 'tools/call', {'name': 'search_faq', 'arguments': {'question': 'What is your return policy?'}}),
            request(3, 'tools/call', {'name': 'get_faq', 'arguments': {'faq_id': 'faq-101'}}),
            request(4, 'tools/call', {'name': 'search_faq', 'arguments': {'question': 'What is the weather?'}})])
        values = [json.loads(r['result']['content'][0]['text']) for r in replies[1:]]
        self.assertEqual(values[0]['faq']['id'], 'faq-101')
        self.assertEqual(values[0]['faq'], values[1]['faq'])
        self.assertFalse(values[2]['matched'])
        self.assertIsNone(values[2]['faq'])

    def test_invalid_args_and_missing_faq(self):
        calls = [
            {'name': 'search_faq', 'arguments': {'question': ''}},
            {'name': 'search_faq', 'arguments': {'question': 'q' * 1001}},
            {'name': 'get_faq', 'arguments': {'faq_id': '../../.env'}},
            {'name': 'get_faq', 'arguments': {'faq_id': 'faq-101', 'path': '/etc/passwd'}},
            {'name': 'delete_reply', 'arguments': {}},
        ]
        replies = self.run_messages([INIT, READY] + [request(i+2, 'tools/call', c) for i,c in enumerate(calls)] + [request(99, 'tools/call', {'name':'get_faq','arguments':{'faq_id':'faq-999'}})])
        self.assertTrue(all(r['error']['code'] == -32602 for r in replies[1:-1]))
        self.assertTrue(replies[-1]['result']['isError'])

    def test_lifecycle_errors_and_unknown_methods(self):
        replies = self.run_messages([request(0, 'tools/list'), INIT, READY, request(2, 'unknown'), request(3, 'ping')])
        self.assertEqual(replies[0]['error']['code'], -32000)
        self.assertEqual(replies[2]['error']['code'], -32601)
        self.assertEqual(replies[3]['result'], {})

    def test_malformed_input_does_not_break_next_request(self):
        replies = self.run_messages(['{bad json', INIT, READY, request(2, 'ping')])
        self.assertEqual(replies[0]['error']['code'], -32700)
        self.assertEqual(replies[2]['result'], {})


class GuardrailTests(unittest.TestCase):
    def test_secret_patterns(self):
        for data in [b'ghp_' + b'A' * 36, b'AKIA' + b'B' * 16, b'-----BEGIN ' + b'PRIVATE KEY-----']:
            self.assertTrue(guardrail.inspect('example.txt', data))

    def test_private_files_and_safe_template(self):
        for name in ['.env', 'config/.env.production', 'data/replies.db', 'data/replies.db-wal']:
            self.assertTrue(guardrail.inspect(name, b'example'))
        self.assertEqual(guardrail.inspect('.env.example', b'DB_PATH=/data/replies.db'), [])
        self.assertEqual(guardrail.inspect('README.md', b'Fictional policy documentation'), [])

    def test_scans_staged_blob_not_working_file_and_redacts_values(self):
        with TemporaryDirectory() as directory:
            def git(*args):
                subprocess.run(['git', '-C', directory, *args], check=True, capture_output=True)
            git('init', '-q')
            path = Path(directory) / 'sample.txt'
            fake = 'ghp_' + 'C' * 36
            path.write_text(fake)
            git('add', 'sample.txt')
            path.write_text('safe unstaged replacement')
            run = subprocess.run([sys.executable, str(ROOT/'agent-hooks/check_staged.py'), directory], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('GitHub token pattern', run.stderr)
            self.assertNotIn(fake, run.stderr + run.stdout)
            git('add', 'sample.txt')
            clean = subprocess.run([sys.executable, str(ROOT/'agent-hooks/check_staged.py'), directory], capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0)

    def test_not_a_repository_fails_closed(self):
        with TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT/'agent-hooks/check_staged.py'), directory], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
