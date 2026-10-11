# Clean-checkout verification

A fresh HTTPS clone of the private GitHub repository at commit
`4e844edde520805b46a7556eb22543608442f8e5` was tested on October 11, 2026 UTC.
A newly created virtual environment installed requirements-dev.txt without
reusing the development environment's site-packages. No application files in
the clone needed editing, and its tracked working tree remained clean.

## Results

| Check | Result |
| --- | --- |
| Install documented dependencies | Passed |
| pip check | No broken requirements |
| Python tests | 53 methods: 51 passed, 2 PostgreSQL tests skipped as documented |
| Frontend tests | All 5 passed |
| Start FastAPI through Uvicorn | Passed |
| HTML and four frontend JavaScript/CSS assets | HTTP 200 |
| Return-policy question | Draft linked to faq-101 |
| Edit, save, list, and retrieve a fictional reply | Passed; save returned HTTP 201 |
| Password-reset question | No match, with no FAQ source |
| Stop and restart the server process | Saved reply remained identical |

[Machine-readable results](evidence/clean-checkout.json) and the
[resolved package list](evidence/clean-checkout-packages.txt) record the run.
The package list is an observation, not a replacement dependency lockfile.

## Procedure and disclosed differences

The run followed the README's local installation and test instructions using
Python 3.12.14 on macOS ARM64. An explicit Python 3.12 executable created .venv;
commands used .venv/bin/python instead of activating it in a shell. Node 24.19.0
was used locally (the README permits 18+; hosted CI uses 22).

A free loopback port replaced 8000 to avoid the existing development server.
The server ran without --reload to permit controlled process shutdown/restart.
The default SQLite database was created only inside the disposable clone.
DATABASE_URL, DB_PATH, RENDER, and TEST_POSTGRES_URL were removed from the test
process environment so inherited settings could not select a live database.
The process was stopped after testing; no hosted records were touched.

This is a fresh checkout and environment on the same computer, not verification
on a second machine, Windows, or Linux. Docker engine execution and PostgreSQL
were not part of this local run; their hosted checks are documented separately.
Docker volume recreation, independent review, course-specific audit tools, and
required peer reviews remain outstanding.
