"""
Django settings for apirechtegewalt project.
"""
import os
import re

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

DEBUG = os.getenv("DEVELOPMENT") == "True"

SECRET_KEY = "secret" if DEBUG else os.getenv("SECRET_KEY")

# https://stackoverflow.com/a/45288019/4028896
ALLOWED_HOSTS = (
    ["*"]
    if DEBUG
    else [".api.tatortrechts.de"]
    + ["172.17.{}.{}".format(i, j) for i in range(256) for j in range(256)]
)

# Application definition

INSTALLED_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.api.v2",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "corsheaders",
    "django_filters",
    "crispy_forms",
    "dbbackup",
    "apirechtegewalt.main",
    "apirechtegewalt.cms",
]

if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
    ]

MIDDLEWARE = [
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "apirechtegewalt.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apirechtegewalt.context_processors.settings",
            ]
        },
    }
]

DEFAULT_FROM_EMAIL = "kontakt@tatortrechts.de"

AUTH_USER_MODEL = "main.User"
CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = "apirechtegewalt.wsgi.application"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Keep connections in the pool for an hour.
CONN_MAX_AGE = 60 * 60

# databasis

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "password",
            "HOST": "db",
            "PORT": 5432,
        }
    }

elif os.getenv("DATABASE_URL"):
    # Running under Dokku.
    USER, PASSWORD, HOST, PORT, NAME = re.match(  # type: ignore
        r"^postgres://(?P<username>.*?)\:(?P<password>.*?)\@(?P<host>.*?)\:(?P<port>\d+)\/(?P<db>.*?)$",
        os.getenv("DATABASE_URL"),
    ).groups()

    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": NAME,
            "USER": USER,
            "PASSWORD": PASSWORD,
            "HOST": HOST,
            "PORT": int(PORT),
        }
    }
else:
    print(
        "Can't connect to the database right now since environment variables are missing."
    )

# caching

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

SESSION_CACHE_ALIAS = "default"
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_AGE = 365 * 24 * 60 * 60
SESSION_COOKIE_SECURE = True

# email

if os.getenv("EMAIL_URL", ""):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT = re.match(  # type: ignore
        r"^email://(?P<username>.*)\:(?P<password>.*?)\@(?P<host>.*?)\:(?P<port>\d+)\/?$",
        os.getenv("EMAIL_URL", ""),
    ).groups()
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
SITE_ID = 1


if not DEBUG:
    # sentry: https://docs.sentry.io/platforms/python/django/
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[DjangoIntegration()])


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        }
    },
}

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "_static")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# wagtails

WAGTAIL_SITE_NAME = "Content for api.tatortrechts.de"
WAGTAILIMAGES_IMAGE_MODEL = "cms.CustomImage"

# DRF

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# backup

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "/backups/"}

# crispy forms

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
