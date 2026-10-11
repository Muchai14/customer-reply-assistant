"""Run the FAQ server through the official MCP SDK, with no model API."""
import asyncio
from datetime import datetime, timezone, timedelta
from importlib.metadata import version
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError

ROOT = Path(__file__).resolve().parents[2]


async def main():
    evidence = {"observed_at": datetime.now(timezone.utc).isoformat(),
                "client": "official MCP Python SDK", "version": version("mcp"), "calls": []}
    parameters = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp-server/server.py")])
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=10)) as session:
            initialized = await session.initialize()
            evidence["protocol"] = initialized.protocolVersion
            discovered = await session.list_tools()
            evidence["tools"] = [tool.name for tool in discovered.tools]
            assert set(evidence["tools"]) == {"search_faq", "get_faq"}
            for name, args in [
                ("search_faq", {"question": "What is your return policy?"}),
                ("get_faq", {"faq_id": "faq-101"}),
                ("search_faq", {"question": "What is the weather?"}),
            ]:
                result = await session.call_tool(name, args)
                assert not result.isError
                value = json.loads(result.content[0].text)
                evidence["calls"].append({"tool": name, "arguments": args, "result": value})
            assert evidence["calls"][0]["result"]["faq"]["id"] == "faq-101"
            assert evidence["calls"][1]["result"]["faq"]["id"] == "faq-101"
            assert evidence["calls"][2]["result"]["matched"] is False
            try:
                await session.call_tool("get_faq", {"faq_id": "../../.env"})
            except McpError as error:
                assert error.error.code == -32602
                evidence["invalid_path_rejected"] = True
            else:
                raise AssertionError("Invalid path was not rejected")
    (ROOT / "docs/evidence/mcp-client-demo.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: official SDK initialization, discovery, FAQ lookups, no-match, invalid argument rejection.")


if __name__ == "__main__":
    asyncio.run(main())
