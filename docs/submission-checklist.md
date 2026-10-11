# Draft Rubric Submission Checklist

This checklist maps the supplied 2026 draft rubric to current evidence. It does not award a grade. Confirm final rules and the October 26 deadline with the course.

| Criterion | Evidence now | Remaining work |
| --- | --- | --- |
| 1 Problem description | README and product specification | Owner review |
| 2 AI-assisted workflow | AI development log with prompts, context, decisions, and checks | Record independent human review |
| 3 Technologies and architecture | README and architecture notes | Render Free + Neon Free documented |
| 4 Frontend | Connected responsive UI, centralized API client, five unit tests | Hosted ecommerce draft/edit/save/history/no-match browser checks passed |
| 5 API contract | Tracked OpenAPI file and response-schema tests | Review final contract alignment |
| 6 Backend | Four structured endpoints with automated tests | Independent review |
| 7 Database | SQLite locally; Neon PostgreSQL in cloud; isolated tests for both | Cloud redeploy persistence verified; owner review pending |
| 8 Containerization | Dockerfile, Compose, named volume, run instructions | Verify volume persistence across container recreation |
| 9 Integration tests | Separate API integration directory and reproduction commands | Hosted/container smoke run passed; independent workflow review pending |
| 10 Deployment | [Live Render demo](https://customer-reply-assistant.onrender.com/) and deployment notes | Final owner review |
| 11 CI/CD | GitHub Actions test/build workflow | CI passed; automatic Render deployment after checks and retained history verified |
| 12 Agent extension pack | Instructions, workflow, specialist definition, tested MCP subprocess and guardrail, permission docs | Real separate subagent, validated plugin package, SDK and hook demos recorded in docs/demo.md; student final-diff review pending |
| 13 Security audit and operations | Bandit/pip-audit reports, remediation, extension notes, storage diagnosis, AI tool/data policy | [PR #1 audit](../security/pr-audit-001.md) recorded as AI self-review; independent review and any course-required open-source AI tool runs remain |
| 14 Reproducibility | [Clean checkout](reproducibility.md): install, tests, HTTP workflow, and SQLite restart persistence passed; cloud deployment verified separately | Independent second-machine check and owner review |
| Peer reviews | No evidence yet | Complete required reviews under final cohort rules |

Extension demonstrations are recorded in docs/extension-demo.md. The reviewer output is explicitly a same-assistant manual prompt run; it is not independent review or proof of permanent desktop-client installation.
