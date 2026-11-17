# Base image for the IEM 4723 AI work.
#
# The Streamlit base image plus an MCP SDK and an LLM client, so Lecture 19
# runs the same way as every other example: pull and go, no build. Build it
# from the ai-dev folder with:
#
#   docker buildx build --platform linux/amd64,linux/arm64 \
#       -t ghcr.io/disys-lab/streamlit-ai-base:latest base --push

FROM ghcr.io/disys-lab/streamlit-base:latest

LABEL org.opencontainers.image.title="IEM 4723 Streamlit AI base"
LABEL org.opencontainers.image.description="The IEM 4723 Streamlit base image plus the MCP SDK and an OpenAI-compatible client, for IEM 4723 Information Systems Design."
LABEL org.opencontainers.image.source="https://github.com/disys-lab/docker_tutorial"

COPY requirements.txt /tmp/requirements-ai.txt

RUN pip install -r /tmp/requirements-ai.txt && rm -rf /root/.cache/pip
