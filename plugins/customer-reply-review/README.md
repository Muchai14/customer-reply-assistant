# Customer Reply Review plugin

A repository-local Codex plugin package containing one reusable review skill
and its portable specialist instructions. It supplements the app's separate
MCP server and Git guardrail; it does not bundle credentials or auto-enable them.

Contents:
- .codex-plugin/plugin.json: plugin manifest, version 0.1.0.
- skills/review-customer-reply-change/SKILL.md: reusable review workflow.
- skills/review-customer-reply-change/references/support-policy-reviewer.md:
  specialist context and permissions.

Use this directory as the plugin source in a compatible client's local-plugin
installation flow. Installation syntax is client/version dependent. This task
validates the package but does not register a marketplace or install it globally.
Alternatively, give an agent the SKILL.md path and ask it to apply the workflow to
a named diff; manual loading is not proof of desktop installation.

Example request: “Use review-customer-reply-change to review API diff
8a70763..4fca53c in this checkout. Delegate the policy review to a separate
read-only subagent, use fictional inputs, and record the actual results.”

Permission scope: read selected project source and diffs; temporary databases
for tests only. No production database, secrets, cloud, customer messaging, or
implicit merge authority. The client must enforce permissions; these instructions
are not a sandbox. No external model API key is required by the package itself.

The bundled reviewer is a versioned copy of custom-agent/support-policy-reviewer.md;
keep it synchronized when updating the plugin. See ../../docs/demo.md for the
recorded Module 5 demonstration and the remaining owner-review step.
