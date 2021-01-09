#!/usr/bin/env bash
set -e
set -x

# loads data from the production

ssh rg "./backupdata.sh"
scp rg:/root/backupdata.json .
scp -r rg:/root/media .
docker-compose run --rm manage bash -c "./manage.py reset_db --noinput && ./manage.py migrate && ./manage.py loaddata backupdata.json"
