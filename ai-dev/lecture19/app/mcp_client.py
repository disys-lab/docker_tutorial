"""Talking to the MCP server.

Two functions. One asks the server what tools it has, the other runs one of
them. Both open a connection, do their one job, and close it, which is the
same thing we did with MySQL in Lecture 18.

The MCP library is written with async def, so each function below has an
async half that does the work and a plain half that runs it. Streamlit does
not know about async, so the app only ever calls the plain half.
"""
import asyncio

from mcp import Client

# "mcp" is the service name in docker-compose.yml, not a machine name.
SERVER_URL = "http://mcp:8000/mcp"


def _run(job):
    """Run one async job and complain in English if the server is not there.

    Without this you get "unhandled errors in a TaskGroup", because the MCP
    library wraps the real problem in a couple of layers. We unwrap it.
    """
    try:
        return asyncio.run(job)
    except Exception as problem:
        while getattr(problem, "exceptions", None):
            problem = problem.exceptions[0]
        raise RuntimeError(f"Could not reach the MCP server at {SERVER_URL}. "
                           f"Is it running? ({problem})")


async def _ask_for_tools():
    async with Client(SERVER_URL) as client:
        return await client.list_tools()


def list_tools():
    """Ask the server what it can do, in the shape the LLM expects.

    Nothing here names a tool. If someone adds a fourth tool to server.py,
    this app picks it up the next time the page runs.
    """
    found = _run(_ask_for_tools())

    tools = []
    for tool in found.tools:
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            },
        })
    return tools


async def _call(name, arguments):
    async with Client(SERVER_URL) as client:
        return await client.call_tool(name, arguments)


def call_tool(name, arguments):
    """Run one tool on the server and hand back what it printed."""
    result = _run(_call(name, arguments))
    return result.content[0].text
