FROM python:3.12

WORKDIR /app

ENV PYTHONPATH="/app:${PYTHONPATH}"

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip && pip install poetry

RUN poetry install --no-root --without dev

COPY . .
