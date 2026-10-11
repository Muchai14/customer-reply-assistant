# Verification Record

## Passed locally

- 47 Python tests: 13 matcher unit test methods, 25 API integration test methods, and 9 extension test methods. The FAQ sample test includes 15 cases within a single method.
- 5 Node frontend tests covering save eligibility, changed-question handling, manual reply sources, duplicate-save prevention, request formatting, and errors.
- API response validation against schemas in the tracked OpenAPI file.
- SQLite persistence across application recreation, history ordering, pagination, invalid inputs, and parameterized storage of SQL-like text.
- Compose configuration validation with `docker compose config --quiet`.
- CI YAML structure and smoke-test Python syntax checks.

These counts describe the latest combined application and extension test run. The latest full suite passed on Python 3.12.14 after security updates. Docker build, startup, and smoke checks subsequently passed on GitHub Actions.

## Browser observations

The actual browser demonstrated question input, source-backed draft generation, editing, saving, opening a history record, no-match handling, and retained history after page reload. Dark blue styling was inspected, and desktop/mobile DOM width checks showed no horizontal overflow at 1280 and 390 pixels.

Browser interaction checks were performed on the earlier market-data scenario. The store-data replacement preserved the UI implementation and passed automated tests, but a new complete browser check of the ecommerce scenario has not yet been recorded. A standalone headless browser test attempt failed to launch; browser checks instead used the in-app browser. It would be incorrect to report the unexecuted headless script as a passing test.

## Outstanding verification

- Fresh-checkout installation on another machine.
- Docker persistence across container recreation; build, startup, and health checks passed on GitHub.
- Automatic cloud deployment after passing checks.
- Real deployment URL and deployment after passing checks.
- Actual PR audit output, image scans, and deployment review. Local Bandit/pip-audit reports, extension notes, and a storage diagnosis are now saved in security/ and ops/.
- MCP-client interoperability, specialist review execution, and hook activation.
- Independent human code/policy review and required peer reviews.

## Reproduce

Follow test commands in [README](../README.md), Docker checks in [DOCKER.txt](../DOCKER.txt), and hosted workflow instructions in [CI.txt](../CI.txt). `ops/smoke_test.py` creates a saved fictional reply and should run against an isolated test instance.

## Hosted CI evidence

The [first run](https://github.com/Muchai14/customer-reply-assistant/actions/runs/38104060196) passed backend tests, frontend tests, security gates, Docker image build, container startup and health checks, and the HTTP smoke workflow. [Job metadata](evidence/github-ci.json) records the tested commit and job outcomes. This run does not establish cloud deployment or volume persistence across container recreation.
