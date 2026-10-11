# Verification Record

## Passed locally

- Fresh-checkout run: 53 Python methods, 51 passed and 2 PostgreSQL tests skipped without TEST_POSTGRES_URL. This includes four request-body-limit tests added after the earlier 47-test run.
- 5 Node frontend tests covering save eligibility, changed-question handling, manual reply sources, duplicate-save prevention, request formatting, and errors.
- API response validation against schemas in the tracked OpenAPI file.
- SQLite persistence across application recreation, history ordering, pagination, invalid inputs, and parameterized storage of SQL-like text.
- Compose configuration validation with `docker compose config --quiet`.
- CI YAML structure and smoke-test Python syntax checks.

These counts describe the latest combined application and extension test run. The latest full suite passed on Python 3.12.14 after security updates. Docker build, startup, and smoke checks subsequently passed on GitHub Actions.

## Browser observations

The actual browser demonstrated question input, source-backed draft generation, editing, saving, opening a history record, no-match handling, and retained history after page reload. Dark blue styling was inspected, and desktop/mobile DOM width checks showed no horizontal overflow at 1280 and 390 pixels.

On October 10, 2026 (PDT), the deployed ecommerce browser flow passed: return-policy source faq-101, draft generation, manual editing, saving reply #1, history after reload, opening its details, and an unmatched gift-wrapping question producing manual-reply mode. The deployed dark blue layout was visually inspected. A standalone headless browser test attempt failed to launch; browser checks instead used the in-app browser. It would be incorrect to report the unexecuted headless script as a passing test.

## Outstanding verification

- Verification on a second machine/OS. Fresh checkout and new-environment verification on this computer passed; see [reproducibility](reproducibility.md).
- Docker persistence across container recreation; build, startup, and health checks passed on GitHub.
- Container image scanning and independent audit. PR #1 self-review and live deployment checks are recorded; local scan reports, extension notes, and storage diagnosis are saved in security/ and ops/.
- Independent specialist review and optional permanent desktop MCP/project-hook activation. Official SDK interoperability and disposable-hook activation are demonstrated in extension-demo.md.
- Independent human code/policy review and required peer reviews.

## Reproduce

Follow test commands in [README](../README.md), Docker checks in [DOCKER.txt](../DOCKER.txt), and hosted workflow instructions in [CI.txt](../CI.txt). `ops/smoke_test.py` creates a saved fictional reply and should run against an isolated test instance.

## Hosted CI evidence

The [first run](https://github.com/Muchai14/customer-reply-assistant/actions/runs/38104060196) passed backend tests, frontend tests, security gates, Docker image build, container startup and health checks, and the HTTP smoke workflow. [Job metadata](evidence/github-ci.json) records the tested commit and job outcomes. This run does not establish cloud deployment or volume persistence across container recreation.

## Render and PostgreSQL evidence

The app is live at https://customer-reply-assistant.onrender.com/ on Render Free
with Neon Free PostgreSQL. Hosted CI run 38105116418 passed all 49 Python test
methods (including 2 real PostgreSQL tests), 5 frontend tests, security gates,
and Docker checks. Deployment details are recorded in deployment.md.

Render automatically deployed commit 6d249ed after CI run 38105424730 passed.
The dashboard showed Live with trigger Auto-Deploy; the browser retained saved
reply #1 after reloading against the new deployment. See
[evidence](evidence/render-deployment.json).
