# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.11.9

FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# System dependencies for psycopg, pandas, and Openpyxl
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libgeos-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately for better layer caching
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip \
    && pip install -r requirements/production.txt

# Copy application code
COPY . /app

# Create non-root user
RUN groupadd --system --gid 1000 fdd \
    && useradd --system --uid 1000 --gid fdd --create-home --shell /bin/bash fdd \
    && mkdir -p /app/staticfiles /app/media /var/lib/fdd/staging \
    && chown -R fdd:fdd /app /var/lib/fdd

USER fdd

EXPOSE 8000

# Default command runs the WSGI server; override in compose for worker/beat
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "gevent", \
     "--worker-connections", "1000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
