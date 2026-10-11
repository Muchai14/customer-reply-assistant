# PR audit 001: API request-body limit

PR: https://github.com/Muchai14/customer-reply-assistant/pull/1

Reviewed base: `8a70763ba07342050f43fdfc0fe17407e9322c71`  
Reviewed implementation: `4fca53cf0f58a55f334368c28302eda91ba74b4e`

## Method and scope

Codex reviewed the actual PR diff against main, the FastAPI route/model integration,
the OpenAPI change, and the four new boundary tests. This is an AI-assisted
self-review by the implementation agent, not an independent human or specialist
review and not a run of an open-source AI PR-review product. Bandit is the separate
deterministic open-source scanner. Review date: October 10, 2026 (PDT).

## Finding and remediation

**Medium: field validation did not bound request buffering.** Valid JSON with
excessive trailing whitespace was fully read before validation and could save a
reply. The temporary-database reproduction used 98,384 bytes: the unprotected
app returned 201 and saved one row. With the middleware it returned 413 and saved
zero rows. See [boundary evidence](reports/request-limit-boundary.json). The
before case deliberately removed only the new middleware from the same app;
no oversized requests were sent to the deployed service.

The middleware counts actual streamed bytes before JSON parsing and stops at
96 KiB. Content-Length cannot bypass it. The limit leaves room for all valid
question/reply fields encoded as escaped Unicode. Requests at exactly the limit
pass through; disconnected requests do not invoke the application. The tracked
and runtime OpenAPI schemas describe the 413 response.

## Review results

- No further blocking defect was identified in the reviewed implementation.
- Storage queries, credentials, and permissions are unchanged by this PR.
- Existing frontend error handling receives the JSON detail message.
- Buffering is bounded per request, but the server may already have allocated
  the incoming ASGI chunk. This is not a bound on total process memory.
- No aggregate rate, concurrent connection, slow-upload, or record-count limit
  is introduced. Public history remains shared and synthetic-only.
- Rejected bodies are not drained by this middleware; the ASGI server handles
  connection cleanup. Deployment/proxy behavior is not load-tested here.

## Verification

Local Python suite: 53 test methods, 51 passed and 2 PostgreSQL methods skipped
because TEST_POSTGRES_URL was not set. The four new methods also passed in a
focused rerun after simplifying contract lookup. Hosted CI runs the PostgreSQL
methods, frontend tests, security gates, and Docker smoke checks; inspect the
PR checks for their final status and exact tested commit.

[Bandit output](reports/request-limit-bandit.json) retains only B404 and B603,
both LOW in the existing local Git guardrail. No new finding was reported in
the request-limit code. No dependency change was made in this PR.

## Release status

PR #1 was merged with owner authorization as ea7ef30 on October 11, 2026 UTC.
Merged-code CI run 38107253673 passed. Live HTTPS checks confirmed normal draft
generation (200), oversized draft rejection (413), and retained saved reply #1.
See [release evidence](../docs/evidence/pr-001-release.json). This confirms the
new behavior is deployed; it is not a load test. Independent review, an
open-source AI review/DevOps tool run if required by the final course rules,
container image scanning, and the other checklist items remain outstanding.
