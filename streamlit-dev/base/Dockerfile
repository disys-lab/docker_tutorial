# Base image for the IEM 4723 Streamlit work.
#
# Python 3.12 with streamlit and the course's data libraries preinstalled, so a
# student image only has to COPY its own app in. Build with:
#
#   docker buildx build --platform linux/amd64,linux/arm64 \
#       -t ghcr.io/disys-lab/streamlit-base:latest base --push

FROM python:3.12

LABEL org.opencontainers.image.title="IEM 4723 Streamlit base"
LABEL org.opencontainers.image.description="Python 3.12 with streamlit, pandas, pymysql and redis preinstalled, for IEM 4723 Information Systems Design."
LABEL org.opencontainers.image.source="https://github.com/disys-lab/docker_tutorial"

WORKDIR /usr/src/app

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements.txt \
    && rm -rf /root/.cache/pip

# Streamlit's default port. Publish it with -p when you run a derived image.
EXPOSE 8501
