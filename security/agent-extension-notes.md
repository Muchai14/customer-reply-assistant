# Agent Extension Security Notes

## Scope

These notes cover the FAQ MCP server, specialist definition, and staged-file guardrail. They are an implementation review and local test summary, not an independent audit or comprehensive security scan.

## Controls and observed checks

- The MCP interface exposes only search_faq and get_faq. Tests confirm tool discovery and reject unknown tools, extra arguments, invalid paths disguised as FAQ IDs, and oversized questions.
- Initialization is required before tool use. Protocol tests exercise startup, errors, notification handling, and subsequent requests after malformed JSON.
- FAQ content is loaded from a fixed project location. The server uses neither the reply database nor HTTP requests. It does not accept caller-selected filesystem paths or shell commands.
- The staged scanner reads the exact Git index version, not the working copy. An isolated Git test demonstrates that replacing a working file does not hide a staged synthetic token.
- Scanner findings identify a filename and rule without printing the matching token. Tests check this redaction and verify that inspection errors block rather than pass.

## Residual risks

A model consuming FAQ text can still be vulnerable to prompt injection; source text must be treated as data, and tool hints are not enforceable permissions. The Python process retains the operating-system privileges of its launcher. Review code and dataset changes before running the server.

The minimal stdio server has no general-purpose input-rate or raw-line-size protection. It is intended for a trusted local client, not direct untrusted network exposure. Protocol coverage is deliberately narrow and real-client interoperability remains unverified.

The hook covers only selected patterns and file types; it will miss many credentials and private data. Git hooks can be bypassed, and a prompt-defined reviewer is not a security sandbox. Use independent open-source scanners and actual reviewer findings for the remaining audit deliverables.

## Pending work

Connect a compatible client and record a real tool lookup; run the reviewer on an actual change; demonstrate the enabled hook; complete deterministic repository/dependency scans, PR audit output, operational diagnosis, and the separate AI tool/data policy.
