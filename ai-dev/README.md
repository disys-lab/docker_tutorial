# ai-dev

The AI material for IEM 4723, Lecture 19.

Everything here runs the image `ghcr.io/disys-lab/streamlit-ai-base`, which is
the Streamlit base image from `streamlit-dev/` plus an MCP SDK and an LLM
client. Nothing has to be built; the image is pulled.

| Folder       | What it is                                   | Open                  |
|--------------|----------------------------------------------|-----------------------|
| `lecture19/` | A chatbot that reads the warehouse data through MCP | http://localhost:8507 |

## Lecture 19: a chatbot that can read the warehouse data

Two columns. You ask a question on the left, and the chart that answers it
turns up on the right. The model does not read the CSV files. It asks an **MCP
server** for numbers, and the app draws them with the same chart calls we used
in Lectures 16 to 18.

```bash
cd lecture19
docker compose up -d
```

Open http://localhost:8507, put your endpoint, key and model name in the
sidebar, and ask something like *which carrier shipped the most orders?*

### What is where

| File | What it does |
|---|---|
| `mcp-server/server.py` | The MCP server. Three tools over three CSV files. Knows nothing about Streamlit |
| `app/mcp_client.py` | Connects to the server, asks what tools exist, runs one |
| `app/main.py` | The page: sidebar, chat on the left, chart on the right |

### The three tools

| Tool | What it answers |
|---|---|
| `list_datasets()` | What data is here |
| `columns(dataset)` | What is in one dataset |
| `summarize(dataset, group_by, how, measure, chart)` | Group the rows and count or add something up |

The datasets are `customers`, `orders` and `items`, read straight from
`mysql-dev/data/orders/`, which is mounted read-only. No database and no joins.

### The one thing worth understanding

The model never runs anything. It reads the tool descriptions, decides which
tool it wants and what to pass, and then **stops and says so**. It is
`app/main.py` that goes and runs the tool, and hands the answer back for the
model to put into words. The tool call appears above the chart so you can see
exactly what it asked for.

Nothing in `app/` names a tool. The list comes from the server at runtime, so
adding a fourth tool to `server.py` is enough for the model to start using it.

### Three things to try

**1. Turn the tools off.** Untick *Let the model use the tools* in the sidebar
and ask the same question. You get a confident, fluent, completely invented
answer, which is the reason the rest of this exists.

**2. Turn them back on.** Same question, real numbers, and a chart.

**3. Stop the server.**

```bash
docker compose stop mcp
```

Ask another question and the app tells you it cannot reach the server. Start it
again and everything works.

```bash
docker compose start mcp
```

The chat and the tools are two separate programs in two separate containers.
That is the whole point of the protocol.

## Endpoints

The sidebar takes any OpenAI-compatible endpoint, so this works with OpenAI,
with a hosted gateway, or with a model running on your own machine.

| | Endpoint | Key |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | your key |
| Ollama, on your machine | `http://host.docker.internal:11434/v1` | anything non-empty |

Your key is kept in `st.session_state` for as long as the tab is open. It is
never written to a file and never sent anywhere except the endpoint you named.

## The base image

Source is in `base/`. It is `streamlit-base` plus the MCP SDK and an
OpenAI-compatible client, and no application code. Rebuild and publish from
this folder with:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
    -t ghcr.io/disys-lab/streamlit-ai-base:latest base --push
```

The `--platform` flag matters: it builds for both Intel and Apple Silicon, so
the image works on every student machine rather than only the one that built it.

It is layered on `streamlit-dev/base`, so rebuilding that one does not update
this one. Build them in that order.

The versions in `base/requirements.txt` are pinned and the comment there says
why: `mcp` 2.x renamed `FastMCP` to `MCPServer`, so a later major version will
not run `server.py`, and the `cryptography` wheels after 46 crash on arm64 Macs
with an illegal instruction the moment MCP touches them.

## Editing while it runs

`app/` and `mcp-server/` are both mounted into their containers, so edits on
your machine take effect immediately. Streamlit offers a rerun when you save.
The MCP server does not reload itself, so restart it after changing a tool:

```bash
docker compose restart mcp
```

## Ports

Chosen so nothing in this repo collides:

| | Here | Elsewhere |
|---|---|---|
| Streamlit | 8507 | 8503 to 8506 (`streamlit-dev`) |
| MCP server | 8600 | |

Inside the compose network the MCP server keeps its standard port, so the app
connects to `mcp:8000` by service name. The published number only matters from
your machine.

## Stopping

```bash
docker compose down
```
