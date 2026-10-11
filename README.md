# Customer Reply Assistant

Customer Reply Assistant helps customer service staff draft, review, and save replies to common online-store questions. Repeatedly looking up return, shipping, and order policies takes time; this application suggests a relevant FAQ and a reply template for a person to review.

The demo uses **Northstar Demo Store**, an entirely fictional shop. Its 12 FAQs cover returns, refunds, exchanges, delivery, shipping costs, tracking, cancellations, address changes, damaged items, incorrect items, and international shipping. No real company or customer data is included.

## What the application does

1. Enter a customer question or choose an example.
2. Match it against the FAQ knowledge base and display a draft with its source.
3. Edit the draft and explicitly save the reviewed reply.
4. Browse saved history and open individual records.

If no FAQ matches, the page explains this and allows a manually written reply. Draft generation does not save a record. Saved replies persist across restarts using SQLite locally or Neon PostgreSQL in the hosted demo. Nothing is sent to customers, and the application cannot process refunds or change orders.

The dark blue frontend is connected to a FastAPI backend. Matching uses deterministic keyword phrases and a fixed reply template, not a language model. AI tools assisted development; the application needs no external AI API key.

## Why save replies?

Saving lets customer service staff revisit previous responses and use them as references when handling similar questions. It also demonstrates the complete application workflow: submit from the frontend, validate in the backend, store in a database, and retrieve the record later.

Each explicit save stores the customer question, final edited reply, FAQ source ID (or null for a manual reply), record ID, and creation time. The current app does not store the original unedited draft, a policy-version snapshot, or an independent approval status. Clicking Save records a response; it does not verify that the response is correct or send it to a customer.

## Future AI-agent use of saved replies

Saved replies provide a foundation for future AI-agent features, such as retrieving reviewed responses and evaluating answer quality. Possible extensions include:

- Retrieve approved answers to similar questions as reference material for a new draft.
- Identify recurring questions and gaps in the FAQ knowledge base.
- Build evaluation cases from verified question-and-answer pairs to check a future agent's accuracy and policy compliance.

**These are future possibilities, not current features.** The current version generates drafts only from the bundled FAQ file. It does not retrieve saved replies during generation, train a model, or learn automatically from its history.

Before using history as an agent knowledge source, add explicit approval and correctness labels, policy versions, and the original draft alongside the final reply. Review records for accuracy and outdated policies. The hosted demo has shared history and no authentication, so a saved record is not automatically trustworthy. Use fictional content here; any future real-business dataset would need authorized use and removal of customer personal information before reuse.

## Current status

The app is live at [Customer Reply Assistant](https://customer-reply-assistant.onrender.com/) on Render Free with Neon Free PostgreSQL storage. Local development supports SQLite. Backend/frontend tests, security gates, Docker build/startup, and the container smoke test passed in GitHub Actions. **Docker volume recreation testing, independent review, and remaining audit artifacts are unfinished.** This is not yet a submission-ready project.

See the [submission checklist](docs/submission-checklist.md) for the full draft-rubric mapping.

## CI/CD — evidence for peer review

**GitHub Actions checks the code; Render deploys it after those checks pass.**
The workflow is named **Test and build** in the [Actions tab](https://github.com/Muchai14/customer-reply-assistant/actions).

```text
Push to main → GitHub tests + security checks → Docker build + smoke checks
            → all checks pass → Render automatic deployment → live app
```

Pull requests also run CI. Render is configured to deploy the main branch with
`autoDeployTrigger: checksPass` in [render.yaml](render.yaml). Deployment runs on
Render, so GitHub Actions does not contain a separate deploy job.

| What to verify | Evidence |
| --- | --- |
| Successful CI and Docker checks | [Merged PR #1 run](https://github.com/Muchai14/customer-reply-assistant/actions/runs/38107253673), commit ea7ef30 |
| Observed Render automatic deployment | [Recorded dashboard evidence](docs/evidence/render-deployment.json): commit 6d249ed, trigger Auto-Deploy, status Live; links its matching successful CI run |
| Deployed PR #1 behavior and persistent history | [Live release checks](docs/evidence/pr-001-release.json): normal draft 200, oversized draft 413, saved reply retained |
| Working application | [Customer Reply Assistant](https://customer-reply-assistant.onrender.com/) |

Reviewers do not need access to the private Render dashboard to read the saved
evidence. These records describe specific verified deployments, not a claim
that every future run will pass. See [deployment instructions](docs/deployment.md)
for reproduction and free-plan limitations. GitHub links require repository access.

## Run locally

Use Python 3.12 to align with the verified dependency set, Docker image, and CI configuration. Earlier Python 3.9 results predate the security dependency update. Initial dependency installation requires internet access.

First check `python3 --version`; it must identify Python 3.12. If your system default differs, use your Python 3.12 executable to create the virtual environment.

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

On Windows, replace the activation command with `.venv\Scripts\Activate.ps1` in PowerShell.

Open [the application](http://127.0.0.1:8000/) or [interactive API documentation](http://127.0.0.1:8000/docs). Keep the terminal running while using the page. Press Ctrl+C to stop it. The frontend is served by FastAPI; no frontend build or Node.js installation is needed to use the app.

Try **What is your return policy?**, edit the returned draft, and save it. Then open it from history. Try **Please reset my password.** to see the no-match behavior.

## Run with Docker

With a working Docker engine and Docker Compose:

```bash
docker compose up --build -d
```

Open the same local URL. The `reply-data` named volume stores the SQLite database. `docker compose down` removes the container while retaining this volume; using `--volumes` would also erase its saved data.

Compose validation, image build, startup, health checks, and the HTTP smoke workflow passed on GitHub Actions. Volume persistence across container recreation still needs verification; the local Docker engine was unavailable. See [Docker instructions](DOCKER.txt) for the remaining verification steps and port configuration.

## Run tests

After installing `requirements-dev.txt`, run from the project root:

```bash
# All backend tests
python -m unittest discover -s backend/tests -v

# Backend unit tests only
python -m unittest backend.tests.test_matcher -v

# API integration tests only
python -m unittest discover -s backend/tests/integration -v
```

Frontend tests require Node.js 18 or newer; CI selects Node.js 22. No npm installation is required:

```bash
cd frontend
node --test tests/*.test.js
```

The latest local results are **51 Python tests passing, 2 PostgreSQL tests skipped without a database URL, and 5 frontend tests passing**. The verified merged PR #1 CI run passed all 53 Python tests, including the two real PostgreSQL tests. Backend tests use temporary databases. Integration tests exercise requests, validation, real SQLite persistence, pagination, and response schemas from the tracked OpenAPI contract. Frontend tests cover state transitions and the centralized API client; they are not automated browser tests.

A [fresh-checkout verification](docs/reproducibility.md) passed installation, tests, the HTTP workflow, and SQLite persistence after restarting the server on macOS. See [verification details](docs/verification.md) for coverage and limitations.

## API contract

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/drafts` | Generate a draft and return its FAQ source |
| POST | `/api/replies` | Save a reviewed reply |
| GET | `/api/replies` | List history with `limit` and `offset` |
| GET | `/api/replies/{id}` | Retrieve one saved reply |

[openapi.yaml](openapi.yaml) was defined before endpoint implementation and is used to validate API responses in tests. Questions accept 1–1,000 characters; saved replies accept 1–5,000, after trimming. Validation failures return 422; a missing record returns 404.

## Architecture and storage

| Component | Role |
| --- | --- |
| HTML, CSS, JavaScript | Responsive page, editing, review state, and history |
| FastAPI and Pydantic | HTTP endpoints and input/output validation |
| Python keyword matcher | Deterministic FAQ selection |
| JSON FAQ file | Fictional store policies and matching phrases |
| SQLite / Neon PostgreSQL | Local / hosted persistent reply storage |
| Docker Compose | One app container and a persistent database volume |
| GitHub Actions | Automated tests, security checks, image build, and smoke checks |

Local runs default to `backend/data/replies.db`. Set `DB_PATH` to choose another file; relative values resolve from the shell's working directory. Docker uses `/data/replies.db`, and tests use temporary locations. `.env` files are not loaded automatically.

Read the [architecture notes](docs/architecture.md) and [detailed run instructions](backend/RUNNING.txt).

## Repository layout

```text
README.md
product-spec.md
AGENTS.md
openapi.yaml
requirements.txt
requirements-dev.txt
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
frontend/                 Page, styles, API client, UI state, and tests
backend/                  API, matcher, database, FAQ data, and tests
docs/                     Architecture, AI workflow, verification, checklist
agent-capabilities/       Reusable review workflow
custom-agent/             Support Policy Reviewer definition
mcp-server/               Read-only FAQ tools over stdio
agent-hooks/              Staged-file guardrail
.githooks/                Optional Git pre-commit wrapper
security/                 Extension security notes
ops/smoke_test.py          HTTP smoke check for disposable test instances
```

## AI-assisted development

The project owner selected scope, requested a simpler implementation without paid model APIs, directed the dark blue redesign, and changed the scenario to ecommerce support. Codex generated and revised code and tests and executed local checks. These product decisions do not imply an independent human code audit. See [the development log](docs/ai-development-log.md) for prompts, context, review, and verification evidence.

## Limitations and remaining work

- Keyword matching does not understand intent, negation, spelling mistakes, or all paraphrases. Multiple topics still produce one FAQ. Every draft needs review.
- This is a single-user fictional demo without login or per-user history isolation. Do not enter personal customer data.
- Each successful save creates a new record. The UI blocks identical repeated saves, but the API is not idempotent; check history before retrying after a lost response.
- FAQs load at startup. Restart or rebuild after changing them. Old market-data FAQ IDs are not reused by the store dataset.
- [Live demo](https://customer-reply-assistant.onrender.com/): Render Free with Neon Free PostgreSQL. See [deployment instructions](docs/deployment.md). The first request after inactivity can be slow.
- The [first CI run](https://github.com/Muchai14/customer-reply-assistant/actions/runs/38104060196) passed, including the [CI workflow](.github/workflows/ci.yml) test and Docker jobs. See [CI instructions](CI.txt).
- The [extension pack](docs/agent-extension-pack.md) now includes a workflow, specialist definition, read-only MCP server, guardrail, and permission notes. [Demonstrations](docs/extension-demo.md) cover official SDK client calls, a real hook in a disposable repository, and a same-assistant reviewer prompt run. Permanent desktop activation and independent review are not claimed. Local security scans, operational diagnosis, and the AI tool/data policy are recorded in the [security report](security/audit-report.md). The scoped [PR #1 audit](security/pr-audit-001.md) is recorded as AI self-review.

The course rubric is a draft. Confirm final requirements, the October 26 submission deadline, and peer-review rules with the course before submitting.

## Free hosting

[Render Free with Neon Free](docs/deployment.md) keeps cloud history in PostgreSQL. Set DATABASE_URL in Render; never commit it. Local SQLite behavior is preserved. Two real PostgreSQL integration tests run in CI; locally they skip without TEST_POSTGRES_URL. The live URL, automatic deployment after passing CI, and saved history across redeployment are verified in the deployment evidence.

## Before publishing the repository

The [credential scan report](security/pre-publication-review.md) records no
Gitleaks findings in the scanned tracked files and fetched Git history. The
repository remains private; owner review and final submission checks are still
required. This scan is not a guarantee that all sensitive information is absent.

## Agent extension pack: demo and evidence

The [Agent Extension Pack — Demo and Evidence](docs/demo.md) includes a real separate policy-review
subagent, a validated [plugin package](plugins/customer-reply-review/README.md),
MCP tool calls, and an actual blocking Git hook. The student still needs to
review the final diff; desktop plugin installation is not claimed.
