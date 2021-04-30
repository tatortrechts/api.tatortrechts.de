FROM python:3.8

ARG DEVELOPMENT=False

ENV DEVELOPMENT $DEVELOPMENT
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get upgrade -y

# for geodjango
RUN apt-get install -y binutils libproj-dev gdal-bin libgdal-dev postgresql-client

RUN pip install --upgrade pip setuptools wheel poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN if [ "$DEVELOPMENT" = "True" ]; then poetry install --no-interaction --no-root ; else poetry install --no-dev --no-interaction --no-root ; fi

COPY dokku/ ./
COPY . .

