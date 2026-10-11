# Agent extension pack demonstration

The following demonstrations ran locally using fictional inputs. No model API,
paid service, real credential, or customer record was needed.

| Component | Observed result | Evidence |
| --- | --- | --- |
| FAQ MCP server | Official Python SDK 1.30.0 initialized the server, discovered both tools, looked up faq-101, handled no match, and rejected a path argument | [Client transcript](evidence/mcp-client-demo.json) |
| Commit guardrail | A real pre-commit hook blocked a synthetic token and then allowed a safe commit | [Hook result](evidence/guardrail-demo.json) |
| Policy reviewer | This assistant applied the portable reviewer prompt to actual PR #1; no new blocking policy defect, with a demonstrated pre-existing negation limitation | [Reviewer output](evidence/policy-reviewer-demo.md) |

## Reproduce

Run from the repository root using Python 3.12 and Git:

```bash
python3 -m venv .venv-extension-demo
.venv-extension-demo/bin/python -m pip install -r ops/demos/requirements.txt
.venv-extension-demo/bin/python ops/demos/mcp_client.py
.venv-extension-demo/bin/python ops/demos/guardrail.py
```

The scripts assert expected outcomes and write the two JSON evidence files.
The SDK is an optional demonstration dependency, separate from application
requirements. The hook script creates and removes its own temporary repository;
it does not change this project's Git hook configuration. It uses a fake token
and does not print its value. Repeating either script updates its timestamped
result, so review that diff before committing it.

For the reviewer, apply custom-agent/support-policy-reviewer.md to a named
change and save the actual findings and limitations. The current output is a
manual prompt-based review by this assistant; it is not an independent agent run.

## Boundaries

SDK interoperability is verified for these calls and this version. No permanent
MCP registration was added to Codex or another desktop client. The hook was
activated only inside the disposable demo repository, not globally or in the
user's project. The matcher still does not understand negation or multiple
intents. Independent review and final course requirements remain to be checked.

SDK reference: [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).
