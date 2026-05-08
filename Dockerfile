# Use official Python slim image for a smaller footprint
FROM python:3.11-slim

# System-level optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

# Install system dependencies for Postgres (psycopg2) and NumPy
RUN apt-get update && apt-get install -y \
	libpq-dev \
	gcc \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

RUN pip install --no-cache-dir poetry

# Set work directory
WORKDIR /code

# Copy dependency files
COPY pyproject.toml poetry.lock* /code/

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . /code/

# Expose Django's default port
EXPOSE 8000
