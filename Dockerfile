FROM node:20-slim AS node_provider
FROM python:3.11-slim

# System-level optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_HTTP_TIMEOUT=180

# Install system dependencies for Postgres (psycopg2) and NumPy
RUN apt-get update && apt-get install -y \
	libpq-dev \
	gcc \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# 3. Copy Node & NPM from Stage 1
# This line specifically pulls the 'node' binary from Stage 1 into Stage 2
COPY --from=node_provider /usr/local/bin/node /usr/local/bin/
# This line pulls the 'npm' source from Stage 1 into Stage 2
COPY --from=node_provider /usr/local/lib/node_modules /usr/local/lib/node_modules
# Link npm so it's globally executable
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set work directory
WORKDIR /code

# Copy dependency files
COPY pyproject.toml poetry.lock* package.json package-lock.json* /code/

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root
RUN npm install

# Copy project files
COPY . /code/

# Expose Django's default port
EXPOSE 8000
