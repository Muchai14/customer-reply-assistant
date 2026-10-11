# AI Assisted Development Log

Codex assisted the project owner with planning, implementation, tests, documentation, and browser checks. This log is reconstructed from the development conversation and tool results; it is not a verbatim transcript or an independent review certificate.

## Process and context

The owner supplied the draft 2026 course rubric and an October 26 deadline. Work was broken into small approved steps: problem description, product specification, API contract, FAQ data, matcher, endpoints, UI, Docker, CI, and documentation.

Context supplied to the assistant included the rubric, agreed scope, previous conversation decisions, and project files read before edits. The OpenAPI contract guided endpoint implementation, and tests compared actual response bodies with its schemas. There were no delegated subagents or external model APIs in the application.

## Development record

| Stage | Owner direction or task summary | AI contribution | Review or verification |
| --- | --- | --- | --- |
| Scope | Choose an easier project and avoid company information | Proposed keyword-based FAQ drafts and fictional data | Owner accepted the smaller scope and requested step-by-step work |
| Language | “all english” | Wrote English project content | Owner refined the target-user wording |
| Contract | Proceed to the next step | Defined four API endpoints and validation rules | YAML and internal references checked; later response-schema tests added |
| Knowledge base | Continue with FAQ preparation | Created fictional FAQ content and 15 expected-match cases | Structural checks and matcher tests |
| Matcher | Implement the next step | Added phrase matching and ranking rules | Unit tests covered cases, boundaries, ties, invalid input, and known limitations |
| Backend | Add draft, save, and history endpoints in sequence | Built FastAPI validation and SQLite repository | API integration tests checked error responses, persistence, pagination, and schema conformance |
| Frontend | Connect the page; make it prettier with a dark blue theme | Built centralized API calls, review state, responsive styles, and history dialog | Frontend unit tests plus browser interaction and layout checks |
| Scenario change | Add return-policy topics; owner preferred ecommerce | Replaced market FAQs with 12 fictional store FAQs and updated examples | 37 backend and 5 frontend tests passed after the change |
| Docker | Make local execution easier | Added Dockerfile, Compose volume, health check, and instructions | Compose validation passed; engine unavailable for runtime verification |
| CI | Add automatic checks | Created tests, Docker build, and smoke-test workflow | Local YAML and Python syntax checks; hosted run still pending |
| Documentation | Record completed work and outstanding requirements | Created README, spec, architecture, log, and checklist | Checked against source files and observed results |

Prompt entries are summaries except quoted phrases. They illustrate task decomposition; they are not claimed to be every prompt used.

## Human and AI review

The owner made product decisions: keep company data out, simplify the application, use English project content, retain human approval of replies, adopt dark blue styling, and switch to ecommerce policies. Acceptance of a step is not evidence that the owner audited each line of code.

The assistant inspected code, generated tests, ran verification commands, and exercised the browser. Some code and its tests were authored by the same assistant, so passing tests cannot substitute for an independent review. Before submission, the owner should run the application, inspect representative changes and fictional policies, and record their own findings. Do not backfill a review that has not happened.

## Corrections and limitations

- After the scenario change, store FAQs received new IDs so existing saved sources were not silently reassigned.
- Shared frontend API calls and review state guard against stale questions and unchanged duplicate saves. Network retries can still create duplicates at the API level.
- Matching is literal and can select irrelevant content or miss paraphrases. It does not reason about policy exceptions.
- Browser checks exercised the core flow on the earlier dataset; the ecommerce change was verified by automated tests. A full browser pass with all store topics remains useful before submission.
- Docker runtime tests, hosted CI, deployment, security audits, and the complete extension pack remain outstanding.

## Data and tools

Used: Codex, local shell and file tools, Python unittest, FastAPI TestClient, JSON Schema checks, Node's built-in test runner, and browser automation for local UI review. Official GitHub documentation informed the CI configuration.

The project uses invented store policies and synthetic questions. No company credentials, private documentation, customer emails, or live order data were required. A separate AI tool/data policy and agent permission document are still needed for the security and extension deliverables.

## Extension pack implementation

Added a portable reviewer definition, a reusable workflow, a read-only FAQ MCP
server, and a staged-file guardrail with permission and security notes. Nine new
tests passed, bringing the Python suite to 46; the five frontend tests still pass.
The MCP server was tested as a subprocess, and the hook scanner against an isolated
Git index. No independent specialist agent was launched, and no MCP client or
repository hook was activated. Actual review output must be collected later.

## Security checks and remediation

Bandit and pip-audit were executed. The original dependency resolution had nine
known advisory records across two packages. After dependency updates and a move
to Python 3.12, the dependency re-scan reported no known vulnerabilities in that
resolution. Two LOW subprocess warnings remain documented in the Bandit report.
An AI-assisted code review reproduced SQLite overflow for oversized history IDs
and offsets; a fix and regression test brought the suite to 47 Python tests, all
passing. Five frontend tests also passed. A temporary storage-path fault and
recovery produced operational evidence. This was not an actual PR audit or an
independent open-source AI reviewer run. See security/audit-report.md.

## Free cloud deployment

The owner selected Render Free and approved transferring the dedicated Neon
connection string into Render DATABASE_URL. Added PostgreSQL storage, kept local
SQLite behavior, required DATABASE_URL on Render, added isolated PostgreSQL tests
to CI, and created render.yaml with checksPass deployment gating. Credentials were
entered through the provider UI and were not committed. The app deployed on the
Free plan; browser checks covered the ecommerce draft/edit/save/history/no-match
workflow. No paid model API or hosting upgrade was enabled.

## Request-body hardening and PR audit

The owner asked for the next project step after free deployment. Codex reviewed
the API boundary, reproduced unbounded JSON whitespace buffering in temporary
databases, added a 96 KiB actual-byte limit and four tests, and opened draft PR #1.
The same agent reviewed its diff; this is explicitly labeled self-review in
security/pr-audit-001.md. No independent human approval is claimed.
