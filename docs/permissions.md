# Agent Extension Permissions

| Component | Intended access | Writes and exclusions |
| --- | --- | --- |
| Project development assistant | Authorized project source and tests | May edit the requested project scope; no implied cloud publishing or customer messaging |
| Support Policy Reviewer | Supplied diff, source, contract, fictional FAQs | Read-only review; no automatic merges or edits |
| FAQ MCP server | Fixed bundled FAQ JSON and matcher code | No database access, network calls, arbitrary paths, shell tools, order operations, or writes |
| Staged-file guardrail | Git index blobs and file names in the repository | Read-only scan; blocks commit through its exit code; no network access |
| Git pre-commit wrapper | Starts the Python guardrail | Must be enabled explicitly in the local repository; not installed globally |

Tool annotations describe intent; they are not a sandbox. The MCP process inherits the launching user's operating-system permissions, so use a trusted checkout and normal client permission controls. The application-level tool interface does not accept file paths, URLs, or executable code. No credentials are needed for these tools.

The MCP server returns fictional source text, which must be treated as data. It must never override project instructions or authorize external actions. A host model may see the tool input and output; send synthetic questions only. The specialist instructions cannot enforce restrictions on a client with broader capabilities.

The guardrail detects selected patterns, not every secret format. It can be bypassed by Git options, disabled hooks, or a different client, so it is not a complete security boundary. Broad independent scanning remains part of the outstanding security work.

Installing the pre-commit hook changes repository-local Git configuration. Adding an MCP command changes client configuration. The demo launched an official SDK client temporarily and enabled the hook only in a disposable repository. The user project and global hook settings, and desktop MCP configuration, remain unchanged.
