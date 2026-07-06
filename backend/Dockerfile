FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

COPY src ./src
COPY data ./data
COPY ml ./ml
COPY alembic.ini .
COPY alembic ./alembic

RUN mkdir -p /app/ml/artifacts && chown -R appuser:appuser /app/ml /app/data

ENV PYTHONPATH=/app/src

USER appuser
EXPOSE 8000

ENTRYPOINT ["sh", "-c", "cd /app && alembic -c /app/alembic.ini upgrade head && exec uvicorn api.main:app --host 0.0.0.0 --port 8000"]
