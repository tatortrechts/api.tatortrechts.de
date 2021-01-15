#!/usr/bin/env bash

docker-compose -f local.yml run --rm manage ./manage.py "$@"
