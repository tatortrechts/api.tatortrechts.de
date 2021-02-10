# `api.tatortrechts.de`

Backend for [tatortrechts.de](tatortrechts.de) ([repo](https://github.com/tatortrechts/tatortrechts.de)).

## Development

```bash
./local.sh [--build]
```

create migrations & migrate database:

```bash
./local_manage.sh
```

import data:

```bash
./local_manage.sh importdata /importdata/rechtegewalt.db
```

reset database and the content:

```bash
./local_manage.sh reset_db
```

access django shell for debugging:

```bash
./local_manage.sh shell_plus --print-sql
```

Restore backup

```bash
./local_manage.sh dbrestore
```

## Deployment

The alpine version of postgis does not work together with Dokku.
So pull & tag this very specific postgres image when creating the postgres db.

```bash
docker pull postgis/postgis:11-3.0
sudo dokku postgres:create apidb -i "postgis/postgis" -I "11-3.0"
```

Mount these volumes:

To 1) import data and 2) store backups, 3) persist image uploads

```
/what/ever:/importdata
/what/ever:/backups
/var/nginx/whatever/media:/app/media
```

Make sure to serve the media files with your nginx.

### Scripts:

```bash
# updatedata.sh
#!/usr/bin/env bash
set -e
set -x

rm -f data/rechtegewalt.db
wget https://data.tatortrechts.de/rechtegewalt.db -P data
dokku run api ./manage.py importdata /importdata/rechtegewalt.db
```

```bash
# backupdata.sh
#!/usr/bin/env bash
set -e
set -x

dokku run api bash -c "./manage.py mediabackup && ./manage.py dbbackup"
```

### Environment Varibales

-   `SENTRY_DNS`
-   `NODEBUG=True`
-   `SECRET_KEY`
-   `WEB_CONCURRENCY=4`

## CMS

We are using [WagTail](https://wagtail.io/) as a headless CMS.
You need to create pages with the following slugs to make the frontend work:

-   `home`
-   `hintergrund`
-   `kontakt`
-   `blog`
-   `projekte`

## License

Affero General Public License 3.0
