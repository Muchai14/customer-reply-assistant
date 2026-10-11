# Agent Extension Pack — Demo and Evidence

This page shows how the project’s coding-agent tools were used: a reusable review
workflow, a separate reviewer subagent, an FAQ MCP tool, and a commit guardrail.
It provides evidence for the Module 5 Agent Extension Pack assignment. These are
development tools; the customer-facing app demo is available at
[Customer Reply Assistant](https://customer-reply-assistant.onrender.com/).

The review uses the existing request-body-limit API change (8a70763..4fca53c).
That change was already merged; this demonstration does not add a new app feature.

| Course demo step | Actual observation | Evidence |
| --- | --- | --- |
| Agent reads project instructions | Parent and separate reviewer read AGENTS.md and permission boundaries | AGENTS.md; reviewer task scope below |
| Reusable workflow invoked | Parent applied agent-capabilities/review-change.md; reviewer also received the packaged skill for manual invocation | [Packaged skill](../plugins/customer-reply-review/skills/review-customer-reply-change/SKILL.md) |
| Specialized subagent reviews API change | A separate /root/policy_reviewer task reviewed the named diff and ran 25 relevant tests | [Actual review](evidence/subagent-review.md) |
| MCP tool called | Official SDK client discovered search_faq/get_faq, looked up faq-101, checked no-match and invalid arguments | [Call evidence](evidence/mcp-client-demo.json) |
| Hook prevents an action | Real pre-commit hook rejected a fake token in a disposable repo, then accepted safe content | [Hook evidence](evidence/guardrail-demo.json) |
| Student reviews final diff | Pending owner review; an AI cannot attest to this step for the student | Review this session's GitHub commit and plugin files |

## Small plugin package

[customer-reply-review](../plugins/customer-reply-review/README.md) includes a
.codex-plugin/plugin.json manifest, a discoverable SKILL.md, and bundled reviewer
instructions. The plugin validator and skill validator passed. The initial
validator invocation using system Python lacked PyYAML; rerunning with the
existing Python 3.12 environment succeeded. No application change was needed.

This is a validated repository-local package, not a claim of desktop installation
or marketplace publication. It needs the target project checkout as review input.
No global settings, production permissions, paid model API, or customer messaging
were added. A real separate AI reviewer ran, but that is not independent human
review. Older same-assistant demo output remains labeled as historical evidence.

## Repeat the demonstration

1. Give a coding agent AGENTS.md and the named diff.
2. Ask it to apply the packaged review-customer-reply-change SKILL.md.
3. Authorize one separate read-only reviewer and save its actual output.
4. Run the MCP and hook scripts using [the existing instructions](extension-demo.md).
5. Review the diff and record your own acceptance or requested corrections.

The SDK demonstration uses real protocol tool calls from a Python client; it does
not claim the FAQ server is permanently registered as a tool in this chat.
