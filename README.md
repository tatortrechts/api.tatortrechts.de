# `api.tatortrechts.de`

Backend for [tatortrechts.de]().

## Development

```bash
./locale [--build]
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
So tag this very specific postgres image:

```bash
sudo dokku postgres:create apidb -i "postgis/postgis" -I "11-3.0"
```

### Usefull commands:

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

### Environment Varibales

-   `SENTRY_DNS`
-   `NODEBUG=True`
-   `SECRET_KEY`
-   `WEB_CONCURRENCY=4`

## CMS

We are using [WagTail](https://wagtail.io/) as a headless CMS.
You need to create pages with the following sluges to make the frontend work:

-   `home`
-   `hintergrund`
-   `kontakt`
-   `blog`

## License

AGPLv3
