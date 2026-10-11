# Actual specialized subagent review

Date: October 11, 2026. Agent task: /root/policy_reviewer.
The parent launched a separate subagent with no inherited conversation history.
It received the project path, reviewer/workflow paths, named diff, and read-only
boundaries. It could inspect source and run isolated local tests, but was told
not to read user databases, credentials, cloud services, or use the network.
These are task instructions, not a claim of OS sandbox isolation or human review.

Reviewed diff: 8a70763..4fca53c. The review is retrospective: PR #1 was already
merged and deployed. No second merge or deployment was performed for this demo.

## Subagent output

Reviewed `8a70763..4fca53c` under the Support Policy Reviewer definition.
**No actionable defect introduced by the request-size change was established.**
Merge readiness is supported within this reviewed scope; the owner decides
whether to merge.

- The middleware enforces actual received bytes before parsing, including
  chunked requests and misleading Content-Length headers
  (backend/request_limits.py:18–29). Exactly 98,304 bytes passes; larger bodies
  receive 413.
- Draft facts remain directly attributable to the selected FAQ: the response
  copies its answer and source ID (backend/main.py:80–83). The diff changes no
  FAQ content, IDs, matcher rules, or frontend review-state rules.
- Manual no-match handling and source-null saves remain functional. No customer
  sending or order-action behavior was introduced.

**Pre-existing observation — informational, not a merge blocker:** literal
matching cannot interpret negation or cover every topic/paraphrase
(backend/matcher.py:53–65).

Concrete reproductions observed:
- “I do not want a refund; can I exchange it?” → faq-103 (Refund Timing).
- “What are your return policy and shipping cost?” → faq-101 only.
- “Could I swap this for a larger one?” → no match.

These follow the current deterministic matching contract and predate this diff.
Suggested follow-up: preserve explicit human review and add these examples to
regression/documentation coverage; semantic ambiguity handling would require a
separate product decision.

**Test evidence:** 25 relevant tests passed using
../../work/security-venv/bin/python: request limits, draft API, and matcher suites.
Additional isolated experiments confirmed:
- Oversized valid save payload: middleware disabled → 201 and one temporary
  record; enabled → 413 and zero records. This was a runtime comparison, not
  execution of the historical checkout.
- No-match → empty draft/null source; subsequent manual source-null save → 201.
- Existing tests cover exact byte limit, disconnect, escaped Unicode at maximum
  field lengths, and 413 contract validation.

**Limitations:** Local in-process verification only; no deployed/proxy testing,
comprehensive security assessment, frontend execution, or human review. The
runner emitted an httpx/TestClient deprecation warning. No files were edited,
no saved user/customer database was accessed, and no credentials, network
services, or external communications were used.

## Follow-up: packaged skill invocation

The same separate subagent then manually read and applied the packaged SKILL.md
and bundled reviewer reference. It confirmed unchanged findings and no concrete
packaging/workflow issue. The bundled reviewer matched the original definition.
Normal acceptance: a valid fictional return-policy question produces a draft
attributed to faq-101, without saving or sending. Boundary acceptance: exactly
98,304 received bytes reach downstream; one additional byte returns 413 before
parsing or saving, independent of Content-Length.

It reused the 25 passing tests without rerunning them. At HEAD 2f765df, a read-only
comparison found no changes from 4fca53c in the reviewed API, matcher, FAQ, contract,
or tested files. The historical checkout was not executed. Manual skill loading
was not desktop installation. No new delegation, edits, integration, or additional
system access occurred. Owner review remains pending.
