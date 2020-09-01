
```bash
docker-compose run --rm manage
```


```bash
docker-compose run --rm manage ./manage.py importdata /importdata/rechtegewalt.db
```

```bash
docker-compose run --rm manage reset_db
```

# Django Startproject Docker Dokku

This is a simple Django 2.0+ project template that uses Docker for development, and deploys to a [Dokku](https://github.com/dokku/dokku) instance.

Based on the work by [Stavros Korokithakis](https://github.com/skorokithakis) for [django-project-template](https://github.com/skorokithakis/django-project-template).


## Features

- Latest Django (hopefully)
- Uses [Poetry](https://poetry.eustace.io/)
- [django-extensions](http://django-extensions.readthedocs.org) for the various useful commands and things
- [Django-dotenv](https://github.com/jpadilla/django-dotenv), so you can easily set environment variables and access
  them in your settings file
- Secure by default (various things won't work on production without TLS)
- Runs under docker-compose, with a PostgreSQL and Redis instance (configured as a cache and session
  backend)


## Installation

Installing the template is easy, you don't really have to do much:

```bash
django-admin.py startproject \
  --template=https://github.com/skorokithakis/django-project-template/archive/master.zip \
  --extension py,cfg,yml,ini,toml \
  <project_name>
```

After installation, you need to change the following:

* Run `poetry lock` to pin the packages to the latest versions.
* Change this README.
* Delete/change the `LICENSE` file.
* Add your domain in `settings.py`'s `ALLOWED_HOSTS`.
* Customize the `.env` file.
* If you're using Dokku, add your domain name to `dokku/CHECKS`.

You're ready to run the project with `docker-compose`:

```bash
$ docker-compose up
```

You should be able to access your project under [http://localhost:8000/](http://localhost:8000/).


## Dokku deployment

The template comes with most of the things you need to deploy it on Dokku. You will need to set up a Postgres database,
a Redis instance and a TLS certificate first, though. For instructions, see my post on [deploying Django projects on
Dokku](https://www.stavros.io/posts/deploy-django-dokku/).


## Production deployment tips

You're going to need to add some secrets for production. That's fine, as long as you don't commit them in any repo. The
project is structured such that all secrets can be passed as environment variables (see the settings file for the
variable names).

You can also specify any secret keys or settings in a `local_settings.py`, which will override your `settings.py` variables. I usually use that for local development.

## License

Copyright © Stavros Korokithakis, Johannes Filter. Licensed under the [MIT license](/LICENSE).
