FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic.ini .
COPY alembic ./alembic

ENV PYTHONPATH=/app/src

USER appuser
EXPOSE 8000

ENTRYPOINT ["sh", "-c", "cd /app && alembic -c /app/alembic.ini upgrade head && exec uvicorn api.main:app --host 0.0.0.0 --port 8000"]
