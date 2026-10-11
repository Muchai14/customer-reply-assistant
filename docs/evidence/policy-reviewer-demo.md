# Support Policy Reviewer demonstration

Reviewer: Codex in the current assistant session, applying
custom-agent/support-policy-reviewer.md as a dedicated manual review prompt.
This was not a separately spawned agent or independent human review.

Scope: PR #1 implementation 4fca53c against base 8a70763, with current
product-spec.md, FAQ data, matcher, API contract, frontend state, and tests.
The change adds request-size protection; it does not change FAQ policy text.
No saved replies, credentials, or cloud services were accessed for this review.

## Findings

No blocking policy regression was established in the request-limit diff.
backend/main.py:82 constructs the draft from the selected FAQ answer, and line 83
attaches that same source. The return-policy example resolves to faq-101. Its
fictional rules require unused items, original packaging, and a request within
30 days, exclude final-sale items, and leave eligibility to a reviewer. The PR
adds no refund, return-approval, sending, or order-action capability.

**LOW, pre-existing limitation:** backend/matcher.py performs literal phrase
matching without negation understanding. “I do not need the return policy. What
is the weather?” still selects faq-101. See policy-reviewer-examples.json for the
observed result. This is not introduced by PR #1 and is consistent with the
specified simple matcher, but demonstrates why a person must review relevance.
Recommended handling: retain the source and human-review step; if semantic
relevance becomes a requirement, add negation/multi-topic acceptance cases
before changing matching behavior. Do not claim semantic understanding.

## Evidence and readiness

The normal return-policy lookup selects faq-101; the plain weather question
returns no match. frontend/state.js:10 requires question consistency before
saving. Existing integration tests exercise manual source-null replies and
unknown FAQ rejection. Four request-limit tests cover the changed boundary,
including valid maximum-length Unicode input. PR #1 CI and merged-code CI passed,
as recorded separately in pr-001-release.json.

The merged change is acceptable within this policy-review scope. This review
is a demonstration of the reusable reviewer instructions, not independent
approval, a comprehensive security audit, or proof of handling every wording.
