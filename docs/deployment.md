# Free Deployment on Render and Neon

Use Render Free for the app and Neon Free for PostgreSQL. Do not add a paid disk,
paid database, custom domain purchase, or paid subscription. Keep usage within
both providers' free allowances; free-plan limits and account checks can change.

## Configuration

The tracked render.yaml declares a single Free Docker web service, port 8000,
health check /api/replies?limit=1, and automatic deployment after CI checks pass.
DATABASE_URL is entered in Render's secret environment settings, never Git.
The app refuses to silently fall back to ephemeral SQLite when RENDER is set.

1. Sign in to Neon and create a dedicated Free project for this demo.
2. Copy the PostgreSQL connection string from Connect. Keep its required TLS
   parameters (for example sslmode=require). Do not paste credentials into chat,
   README, logs, or source files.
3. In Render, connect only the customer-reply-assistant GitHub repository and
   create a Blueprint from render.yaml. Review that the service says Free/$0.
4. Enter the Neon connection string for DATABASE_URL using Render's secret field.
5. Deploy and verify the generated HTTPS URL, draft generation, saving, and history.
6. Restart/redeploy and confirm a synthetic saved reply still exists in Neon.

Free Render services sleep after inactivity, so the first request can be slow.
Render's monthly free instance allowance is shared across the workspace; existing
services also consume it. Do not upgrade or suspend other projects automatically.
All demo users share the same history. Enter synthetic content only.

## Database selection

DATABASE_URL selects PostgreSQL. Without it, local development uses SQLite through
DB_PATH. Existing SQLite records are not automatically migrated; the hosted demo
starts with a separate database. API contracts and page behavior are unchanged.

CI creates disposable PostgreSQL 17, exercises save/history/pagination/restart,
and audits the PostgreSQL driver with the other dependencies. To run these tests
locally, set TEST_POSTGRES_URL to a disposable database where the test user can
create schemas. Each test creates and drops only its own randomized test schema.
Never point the test environment at a production database.

## Status

Deployment configuration and PostgreSQL support passed hosted CI at commit
cddaad2 (run 38105116418), including the real PostgreSQL integration tests,
security checks, frontend tests, and Docker startup/HTTP smoke check.
The dedicated customer-reply-assistant Neon project was created on the Free plan.
Render deployed commit cddaad2 successfully on October 10, 2026 (PDT).
Live URL: https://customer-reply-assistant.onrender.com/
Service: srv-db5f8no473hc73auq1tg (Docker, Free).
Initial deploy: dep-db5f8o0473hc73auq690 (Blueprint trigger, Live).
Browser checks verified FAQ draft generation, editing, saving synthetic reply #1,
and retained history after a page reload. Commit 6d249ed then passed CI run
38105424730 and automatically deployed as dep-db5fahbbc2fs738neeq0. Render showed
"Deploy succeeded | Live" and trigger "Auto-Deploy". A fresh browser reload after
that deployment retained synthetic reply #1, verifying cloud storage persistence.
See evidence/render-deployment.json for the observed identifiers and checks.

References:
- https://render.com/docs/free
- https://render.com/docs/blueprint-spec
- https://neon.com/docs/connect/connect-from-any-app

## Request-limit release

PR #1 merged as ea7ef30; merged-code CI run 38107253673 passed. Public HTTPS
checks on October 11, 2026 UTC verified the new 413 response, normal return-policy
drafts, and retained reply #1. See [release evidence](evidence/pr-001-release.json).
