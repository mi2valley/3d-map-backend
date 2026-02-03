FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl build-essential git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main && \
    poetry cache clear pypi --all

COPY . .
EXPOSE 8080

ENTRYPOINT [ "gunicorn", "backend.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--pythonpath", "/app/src" ]
