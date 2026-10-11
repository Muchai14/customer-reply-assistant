# Review a Customer Reply Assistant Change

Use this repeatable workflow before accepting a code or FAQ change.

1. Read AGENTS.md, product-spec.md, openapi.yaml, and the proposed diff. Identify the intended behavior and affected API, policy, or UI state.
2. State acceptance examples, including one edge case. For FAQ changes, include paraphrases, no-match questions, and collisions with other FAQs. Keep all examples fictional.
3. Implement only the requested scope. Preserve existing records and FAQ identity. Keep backend calls in api.js, SQL parameterized, and UI rendering as text.
4. Run relevant unit/integration tests. Use an isolated database for experiments. For UI changes, inspect the browser at desktop and mobile widths. Record failures as well as passes.
5. Run the read-only review using custom-agent/support-policy-reviewer.md. If a client supports specialist delegation, the owner can assign that definition; otherwise use it as a manual review prompt. The definition alone is not evidence that a review occurred.
6. Inspect staged files with `python3 agent-hooks/check_staged.py` before committing. Resolve findings; do not silently bypass the hook.
7. Report changes, observed verification, unresolved findings, and deployment status. Do not claim hosted CI, security scans, or human review without evidence. The owner controls publishing and merge decisions.

Reusable prompt:

> Review this change against the Customer Reply Assistant product specification and API contract. Use the Support Policy Reviewer definition. Trace each customer-facing claim to a fictional FAQ source, inspect the human-review boundary, and report concrete findings with tests and limitations. Do not modify files or access real customer data.
