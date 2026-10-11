# Project Instructions

## Product scope

Build Customer Reply Assistant for Northstar Demo Store, a fictional ecommerce demo. Keep project content in English and retain the dark blue theme. Drafts use deterministic FAQ matching; no paid model API, real customer data, company documents, automatic sending, or real order actions are in scope.

## Structure

- Keep all frontend backend calls in frontend/api.js and review-state rules in frontend/state.js.
- Keep HTTP routes in backend/main.py, validation in backend/models.py, and SQL in backend/database.py.
- Treat openapi.yaml as the agreed contract; update it alongside endpoint changes and contract tests.
- Use textContent for untrusted UI text and parameterized SQL for database values.
- Use a separate temporary SQLite database for every test application. Never delete or overwrite the user's saved-reply database to run tests.
- Do not reuse existing FAQ IDs for unrelated content. Document dataset changes and preserve saved replies.

## Verification

Run checks appropriate to changed behavior:

```bash
python -m unittest discover -s backend/tests -v
```

From frontend:

```bash
node --test tests/*.test.js
```

Report what ran and any unverified work accurately. Do not claim container execution, security scans, hosted CI, deployment, or human review without observed evidence. Keep documentation status current. Use docs/agent-extension-pack.md for the workflow, reviewer definition, read-only tools, and optional Git hook. Consult docs/permissions.md before enabling integrations.
