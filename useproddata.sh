#!/usr/bin/env bash
set -e
set -x

# loads data from the production

ssh rg "./exportjson.sh"
scp rg:/root/data.json .
scp -r rg:/var/www/rg-media media
docker-compose run --rm manage bash -c "./manage.py reset_db --noinput && ./manage.py migrate && ./manage.py loaddata data.json"
