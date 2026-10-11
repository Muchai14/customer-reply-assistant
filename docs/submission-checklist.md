# Draft Rubric Submission Checklist

This checklist maps the supplied 2026 draft rubric to current evidence. It does not award a grade. Confirm final rules and the October 26 deadline with the course.

| Criterion | Evidence now | Remaining work |
| --- | --- | --- |
| 1 Problem description | README and product specification | Owner review |
| 2 AI-assisted workflow | AI development log with prompts, context, decisions, and checks | Record independent human review |
| 3 Technologies and architecture | README and architecture notes | Final hosting/CD design |
| 4 Frontend | Connected responsive UI, centralized API client, five unit tests | Final ecommerce browser review |
| 5 API contract | Tracked OpenAPI file and response-schema tests | Review final contract alignment |
| 6 Backend | Four structured endpoints with automated tests | Independent review |
| 7 Database | SQLite, configurable DB_PATH, temporary test databases, persistence tests | Verify hosted persistent storage |
| 8 Containerization | Dockerfile, Compose, named volume, run instructions | Run image and verify persistence in Docker |
| 9 Integration tests | Separate API integration directory and reproduction commands | Hosted/container smoke run |
| 10 Deployment | No deployed URL | Select host and deploy with proof |
| 11 CI/CD | GitHub Actions test/build workflow | First successful run and automatic deployment after checks |
| 12 Agent extension pack | Instructions, workflow, specialist definition, tested MCP subprocess and guardrail, permission docs | Client activation and independent reviewer/hook demonstration |
| 13 Security audit and operations | Bandit/pip-audit reports, remediation, extension notes, storage diagnosis, AI tool/data policy | Actual PR audit output and any course-required open-source AI tool runs |
| 14 Reproducibility | Local run/test instructions, Docker and CI notes | Clean-checkout and end-to-end deployment verification |
| Peer reviews | No evidence yet | Complete required reviews under final cohort rules |

The extension pack files are present and locally tested, but have not been activated in an agent client. Local tests and extension notes are not substitutes for independent audit artifacts, an actual reviewer run, or deployment evidence.
