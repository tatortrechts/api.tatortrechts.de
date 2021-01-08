# `api.tatortrechts.de`

Based on [django-startproject-docker-dokku](https://github.com/jfilter/django-startproject-docker-dokku).

## Development

```bash
git cone xx && cd xx && touch .env
```

migrate database:

```bash
docker-compose run --rm manage
```

import data:

```bash
docker-compose run --rm manage ./manage.py importdata /importdata/rechtegewalt.db
```

reset database and it's content:

```bash
docker-compose run --rm manage  ./manage.py reset_db
```

access django shell for debugging:

```bash
docker-compose run --rm manage  ./manage.py shell_plus --print-sql
```

## Deployment

The alpine version of postgis does not work together with Dokku.

```bash
sudo dokku postgres:create apidb -i "postgis/postgis" -I "11-3.0"
```

```bash
sudo dokku run api ./manage.py reset_db
```

```bash
sudo dokku run api ./manage.py migrate
```

```bash
sudo dokku run api ./manage.py importdata /importdata/rechtegewalt.db
```

```bash
sudo dokku run api ./manage.py syncautocomplete
```

## CMS

We are using [WagTail](https://wagtail.io/) as a headless CMS.
You need to create pages with the following sluges to make the frontend work:

-   `home`
-   `hintergrund`

## License

GPLv3
