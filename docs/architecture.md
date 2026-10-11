# System Architecture

The frontend and backend run on the same origin. FastAPI serves the HTML at `/`, static frontend files at `/assets`, and the four API endpoints under `/api`. A separate Node server, frontend build, CORS configuration, or database service is not required for this implementation.

```text
Browser
  index.html and styles.css
  app.js → state.js (review and save eligibility)
  app.js → api.js (all HTTP calls)
                 ↓
FastAPI main.py → models.py (validation)
       ├── matcher.py → data/faqs.json (loaded at startup)
       └── database.py → SQLite replies table
```

## Request flow

`POST /api/drafts` validates the question, runs the matcher, and constructs a typed matched or unmatched response. It does not insert a database row. Matching selects the longest complete keyword phrase; repeated phrases do not increase its score.

`POST /api/replies` validates the reviewed content and checks that a supplied FAQ ID exists. The repository inserts a row with parameterized SQL and returns it after the transaction commits. The server cannot establish whether a person actually reviewed the answer or whether the edited text remains supported by its source.

The history endpoints use short-lived SQLite connections. List count and page results share a read transaction, with ordering by timestamp and ID. The detail endpoint returns 404 if the ID does not exist.

## Storage and environments

| Environment | Database configuration |
| --- | --- |
| Direct local run | Source-relative `backend/data/replies.db` by default |
| Custom local or hosted run | `DB_PATH` environment variable |
| Docker Compose | `/data/replies.db` in the named `reply-data` volume |
| Automated tests | A separate temporary file per test application |

The `create_app` factory accepts an explicit database path for isolation. Initialization uses `CREATE TABLE IF NOT EXISTS`; it preserves existing records but is not a schema-migration framework. Future schema changes need an explicit migration.

The store dataset uses new FAQ IDs to avoid repointing older saved market-data references. Historical responses preserve their text and source ID; source text itself is not versioned in the database.

## Packaging and automation

The Docker image uses Python 3.12 and runs as a non-root user. One container serves the frontend and backend. The health check reads a small history page, exercising HTTP and database access. Compose binds to localhost and keeps data in a named volume.

The CI workflow installs dependencies, runs Python and Node tests, then builds and checks the container only after tests pass. Its disposable smoke test exercises webpage assets and draft-save-history behavior. It is not a deployment pipeline yet.

## Deployment boundary

Render Free is configured in render.yaml; live provisioning is pending. DATABASE_URL selects the PostgreSQL repository for Neon Free, while local runs can retain SQLite. A deployment must provide persistent storage at `DB_PATH`, route traffic to the app, and run only after successful verification. Authentication and multi-user isolation are outside the current demo. No horizontal scaling or multi-instance SQLite design has been implemented.
