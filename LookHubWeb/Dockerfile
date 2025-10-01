FROM python:3.12-alpine

RUN apk update && apk add --no-cache build-base gcc musl-dev libffi-dev tzdata

RUN pip install poetry

ENV PATH="/root/.local/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH=/lookhubweb
ENV TZ=Europe/Moscow

WORKDIR /lookhubweb

COPY docker/app.sh ./docker/
COPY pyproject.toml poetry.lock alembic.ini ./

RUN poetry install --no-interaction --no-root

COPY . /lookhubweb

RUN adduser --disabled-password --gecos '' celeryuser
RUN chown -R celeryuser:celeryuser /lookhubweb
USER celeryuser
