from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "apirechtegewalt.main"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import apirechtegewalt.main.signals  # noqa
