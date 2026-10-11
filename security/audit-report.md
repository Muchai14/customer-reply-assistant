# Security Review and Scan Results

## Scope and outcome

This local review covers the Python application, FAQ MCP server, staged-file guardrail, resolved application/test dependencies, and selected HTTP boundary behavior. It is AI-assisted review plus deterministic open-source scans, not an independent security certification or an actual GitHub PR audit.

The original dependency resolution contained nine known vulnerability records across Starlette and AnyIO. After upgrading runtime dependencies, pip-audit reported no known vulnerabilities in the resolved application/test package set. This reflects the advisory database queried at scan time, not a guarantee about unknown vulnerabilities or future dependency resolutions.

## Findings and fixes

| Finding | Evidence | Resolution |
| --- | --- | --- |
| Old Starlette and AnyIO versions | [Before dependency report](reports/dependencies-before.json): Starlette 0.46.2 and AnyIO 4.12.1 | Updated FastAPI to 0.143.0, Uvicorn to 0.54.0, Starlette to 1.7.0, AnyIO to 4.15.1; [after report](reports/dependencies-after.json) has no reported vulnerabilities |
| Oversized integers caused HTTP 500 | [Before requests](reports/boundary-before.json): an ID or offset of 9223372036854775808 overflowed SQLite binding | IDs above SQLite's range return 404; offsets beyond the total return an empty page without binding the offset; [after requests](reports/boundary-after.json) return 404/200; regression test added |
| Git executable selected by a partial path | Bandit B607 in [before scan](reports/bandit-before.json) | Resolve Git with shutil.which and fail closed if unavailable |
| Subprocess import and invocation | B404 and B603 in [after scan](reports/bandit-after.json) | Two LOW-severity findings retained for review; Git calls use an argument list, no shell, fixed operations, and staged paths as data. The local PATH and Git executable must be trusted. No suppression comments were added |

The original Starlette findings include URL construction, multipart handling, file-range parsing, Windows static-file handling, and endpoint dispatch advisories. Some affected paths are not used by this app, but dependencies were updated instead of assuming non-exploitability. The complete advisory identifiers and fix versions are preserved in the original JSON.

## Tools and reproducibility

Use Python 3.12 in a virtual environment:

```bash
python -m pip install -r requirements-dev.txt -r security/requirements-audit.txt
python -m bandit -r backend agent-hooks mcp-server -x backend/tests -f json -o security/reports/bandit-after.json
python -m pip_audit -r requirements-dev.txt --format json --output security/reports/dependencies-after.json
python -m unittest discover -s backend/tests -v
```

Bandit returns a nonzero exit status while the retained LOW findings remain. Review that report; do not call it a clean scan. The first scan used Bandit 1.8.6 and pip-audit 2.9.0 on Python 3.9. The final scan used Bandit 1.9.4 and pip-audit 2.10.1 on Python 3.12.14. Tool/runtime changes are disclosed because these are not strictly identical before/after environments.

The dependency report includes resolved versions. Direct dependencies and selected runtime dependencies are pinned, but the project does not yet have a complete hashed cross-platform lockfile. Repeat the scan in CI and on the deployment runtime.

## Verification

All 47 Python tests and 5 frontend tests passed after remediation. A storage fault was reproduced and recovered in temporary directories; see [operational diagnosis](../ops/diagnosis.md). No live customer records were used. The API test client currently emits an upstream HTTPX deprecation warning; tests pass, and this is a maintenance note rather than a security finding.

## Remaining gaps

- Repository and hosted CI now exist. This historical scan report is not itself a PR review; see the separate request-body-limit PR audit for the new hardening change.
- No independent reviewer run, full secret-history scan, container image vulnerability scan, live penetration test, has been completed. Free deployment and persistence checks are documented in docs/deployment.md.
- The app has no authentication or user isolation. Use synthetic content only; the hosted demo is public with owner authorization. Request-size limits are prepared in a separate hardening PR; authentication and rate controls remain outside the implemented scope.
- MCP raw input limits, rate controls, and save idempotency remain potential hardening work. Current tool scope and permissions are documented separately.
- No open-source AI PR-review or AI DevOps integration has been exercised. If final course rules require particular tools, run those and preserve their actual output.

See [AI tool and data policy](ai-tool-data-policy.md) and [extension notes](agent-extension-notes.md).
