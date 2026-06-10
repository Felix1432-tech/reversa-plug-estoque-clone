FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy AS base

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir . && \
    playwright install chromium --with-deps

COPY alembic.ini .
COPY alembic/ alembic/
COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
