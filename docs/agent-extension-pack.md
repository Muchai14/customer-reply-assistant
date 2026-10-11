# Agent Extension Pack

This pack supports development and review of Customer Reply Assistant. It is separate from the FAQ assistant inside the application.

## Components

| Requirement | Implementation |
| --- | --- |
| Project instructions | [AGENTS.md](../AGENTS.md) |
| Reusable workflow | [Review a change](../agent-capabilities/review-change.md) |
| Specialist definition | [Support Policy Reviewer](../custom-agent/support-policy-reviewer.md) |
| MCP tool server | [Read-only FAQ server](../mcp-server/server.py) |
| Hook or guardrail | [Staged-file scanner](../agent-hooks/check_staged.py) and [.githooks/pre-commit](../.githooks/pre-commit) |
| Small plugin package | [Customer Reply Review](../plugins/customer-reply-review/README.md) |
| Permission notes | [Permissions](permissions.md) |

## Use the MCP server

Requires Python 3.9 or newer and no third-party dependencies. Configure a stdio MCP client to launch:

```text
python3 /absolute/path/to/customer-reply-assistant/mcp-server/server.py
```

Replace the path with your checkout location. The client should negotiate protocol version `2025-06-18`. The server supports initialization, ping, tool discovery, and tool calls; it does not implement HTTP, resources, prompts, subscriptions, or model sampling. Logs must not be written to stdout.

A typical client configuration shape is shown below; adapt to your client's supported configuration format. This example has not been installed:

```json
{
  "mcpServers": {
    "northstar-faq": {
      "command": "python3",
      "args": ["/absolute/path/to/customer-reply-assistant/mcp-server/server.py"]
    }
  }
}
```

Tools:

- `search_faq` accepts `{"question":"What is your return policy?"}` and returns one candidate FAQ or no match.
- `get_faq` accepts `{"faq_id":"faq-101"}` and returns that FAQ or a tool error when not found.

The server loads fixed local data at startup. It cannot read history, issue refunds, open arbitrary files, or contact services. Restart after FAQ edits. This is a small educational implementation of the tools subset, not a fully certified MCP implementation; interoperability with the official Python SDK 1.30.0 is demonstrated for discovery and these calls; see [the demo](extension-demo.md).

Protocol references: [stdio transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle), and [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

## Use the guardrail

From a Git checkout, scan the actual staged content:

```bash
python3 agent-hooks/check_staged.py
```

To enable the supplied pre-commit wrapper for this repository, first check for an existing hook configuration. Integrate existing hooks instead of replacing them without review:

```bash
git config --local --get core.hooksPath
```

If no existing hook setup needs preserving, enable this one:

```bash
git config --local core.hooksPath .githooks
```

The scanner blocks selected GitHub-token, AWS access-key, and private-key patterns; staged environment secret files; runtime SQLite files; and files larger than its inspection limit. Findings print only the filename and rule, never the matched secret. It reads the index so unstaged edits cannot hide staged secrets. It does not modify files or the index.

## Demonstrate the pack

1. Run the automated extension tests with `python -m unittest discover -s backend/tests -v`.
2. Connect a compatible MCP client and show discovery plus a return-policy lookup.
3. Use the reviewer prompt against a real project change and retain its actual output.
4. In a disposable Git repository, stage a synthetic blocked pattern and confirm the hook stops the commit; never use a real credential.
5. Record the demonstrated results and outstanding limitations.

The [recorded demonstration](extension-demo.md) verifies the server through the official MCP SDK and activates the real hook in a disposable repository. This assistant also applied the reviewer instructions as a manual review prompt. The earlier demonstration did not use a separate reviewer. The newer agent extension pack demo below records an actual separate subagent; permanent desktop MCP registration and project-wide hook installation are still not claimed.

## Module 5 completion update

A real separate reviewer subagent has now run, and a validated plugin package
is included. See [Agent Extension Pack — Demo and Evidence](demo.md) and actual reviewer output. This
supersedes the earlier missing-subagent status; the earlier manual review remains
accurately labeled. The student final-diff review remains pending.
