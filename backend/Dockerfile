FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.lock ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.lock

COPY alembic.ini pyproject.toml ./
COPY alembic ./alembic
COPY app ./app
COPY tests ./tests

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.etl.seed_admin && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
