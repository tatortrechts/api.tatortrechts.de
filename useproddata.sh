#!/usr/bin/env bash
set -e
set -x

# loads data from the production
rsync -rv rg:/root/dokku-backups/ misc/backups
docker-compose run --rm manage ./manage.py dbrestore
