FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get upgrade -y

# for geodjango
RUN apt-get install -y binutils libproj-dev gdal-bin libgdal-dev postgresql-client

RUN pip install -U --pre pip poetry
ADD poetry.lock /app/
ADD pyproject.toml /app/
RUN poetry config virtualenvs.create false
WORKDIR /app

RUN /bin/bash -c '[[ -z "${IN_DOCKER}" ]] && poetry install --no-interaction --no-root || poetry install --no-dev --no-interaction --no-root'

ADD dokku/ /app/

COPY . /app/
RUN /app/manage.py collectstatic --noinput
