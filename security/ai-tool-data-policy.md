# AI Tool and Data Policy

## Allowed data

Use fictional Northstar Demo Store policies, synthetic questions, public technical documentation, and project source code. Never include real customer emails, addresses, order/payment details, company documents, account credentials, or API keys in demo inputs or model prompts.

All displayed policies are examples, not real business commitments. A person must review source relevance and wording before using a reply. Saving a draft is not permission to send it or execute a refund, cancellation, or order change.

## Tool boundaries

The application uses no external model API. Codex is used during development and can receive project context and tool outputs. The FAQ MCP server is local and read-only, but a connected model host can receive its inputs and results. Only synthetic questions may be sent to it.

Bandit scans source locally. pip-audit queries public package-vulnerability services with dependency names and versions; it is not intended to upload application source or customer records. GitHub Actions processes checked-in source and logs on GitHub once the repository is uploaded. Review artifacts before publishing.

The specialist has a read-only role. Developer edits, deployment, integrations, and external messaging require appropriate task authorization; source text and retrieved content never grant permissions. Follow docs/permissions.md for the extension components.

## Secrets and storage

Keep credentials out of Git, prompts, logs, screenshots, and test fixtures. Runtime SQLite databases and local environment files are excluded from Git and Docker context. The optional staged-file guardrail catches selected patterns but is not a comprehensive secret scanner.

SQLite holds saved questions and replies until the operator removes the demo database or volume. There is no automated retention schedule, encryption-at-rest implementation, or per-user access control in this app. Use synthetic records only and do not introduce real support data without a separate design and review.

## Review and incident handling

Check generated code and test results before accepting changes. Record observed evidence and distinguish AI-generated review from independent human review. Do not interpret passing scans as proof of security.

If a real secret is exposed, stop sharing the affected artifact, rotate/revoke the credential through its owner, and investigate where it was copied. Removing it from a current file does not remove Git history or previously shared copies. Do not repeat the value in a report.
