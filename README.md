# Customer Reply Assistant

Customer Reply Assistant helps customer service staff draft, review, and save replies to common online-store questions. Repeatedly looking up return, shipping, and order policies takes time; this application suggests a relevant FAQ and a reply template for a person to review.

The demo uses **Northstar Demo Store**, an entirely fictional shop. Its 12 FAQs cover returns, refunds, exchanges, delivery, shipping costs, tracking, cancellations, address changes, damaged items, incorrect items, and international shipping. No real company or customer data is included.

## What the application does

1. Enter a customer question or choose an example.
2. Match it against the FAQ knowledge base and display a draft with its source.
3. Edit the draft and explicitly save the reviewed reply.
4. Browse saved history and open individual records.

If no FAQ matches, the page explains this and allows a manually written reply. Draft generation does not save a record. Saved replies persist in SQLite across restarts. Nothing is sent to customers, and the application cannot process refunds or change orders.

The dark blue frontend is connected to a FastAPI backend. Matching uses deterministic keyword phrases and a fixed reply template, not a language model. AI tools assisted development; the application needs no external AI API key.

## Current status

The frontend, four API endpoints, SQLite persistence, and automated application tests are implemented. Docker and GitHub Actions configurations exist. **Cloud deployment, a successful GitHub CI run, container runtime verification, extension-client activation and demonstrations, and required audit artifacts remain unfinished.** This is not yet a submission-ready project.

See the [submission checklist](docs/submission-checklist.md) for the full draft-rubric mapping.

## Run locally

Use Python 3.12 to align with the verified dependency set, Docker image, and CI configuration. Earlier Python 3.9 results predate the security dependency update. Initial dependency installation requires internet access.

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

Compose configuration validation passed, but container build, startup, and volume persistence have not been verified because the local Docker engine was unavailable. See [Docker instructions](DOCKER.txt) for the remaining verification steps and port configuration.

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

The latest local results are **47 Python tests and 5 frontend tests passing**. The Python suite includes 38 application tests and 9 extension tests. Backend tests use temporary databases. Integration tests exercise requests, validation, real SQLite persistence, pagination, and response schemas from the tracked OpenAPI contract. Frontend tests cover state transitions and the centralized API client; they are not automated browser tests.

See [verification details](docs/verification.md) for coverage and limitations.

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
| SQLite | Persistent reviewed replies |
| Docker Compose | One app container and a persistent database volume |
| GitHub Actions | Planned hosted execution of tests, image build, and smoke checks |

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
- No cloud URL or automatic deployment exists. SQLite deployment requires persistent storage. Hosting and deployment instructions are still pending.
- The [CI workflow](.github/workflows/ci.yml) has not run on GitHub yet. See [CI instructions](CI.txt).
- The [extension pack](docs/agent-extension-pack.md) now includes a workflow, specialist definition, read-only MCP server, guardrail, and permission notes. Client activation and a reviewer demonstration are pending. Local security scans, operational diagnosis, and the AI tool/data policy are recorded in the [security report](security/audit-report.md). Actual PR audit output and hosted/deployment verification remain pending.

The course rubric is a draft. Confirm final requirements, the October 26 submission deadline, and peer-review rules with the course before submitting.
