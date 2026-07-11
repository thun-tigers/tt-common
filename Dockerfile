FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY tt_common ./tt_common

RUN pip install --no-cache-dir .
