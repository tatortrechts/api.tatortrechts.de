FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get upgrade -y

# for geodjango
RUN apt-get install -y binutils libproj-dev gdal-bin libgdal-dev

RUN pip install -U --pre pip poetry
ADD poetry.lock /code/
ADD pyproject.toml /code/
RUN poetry config virtualenvs.create false
WORKDIR /code

RUN /bin/bash -c '[[ -z "${IN_DOCKER}" ]] && poetry install --no-interaction --no-root || poetry install --no-dev --no-interaction --no-root'

ADD dokku/CHECKS /app/
ADD dokku/* /code/

COPY . /code/
RUN /code/manage.py collectstatic --noinput
