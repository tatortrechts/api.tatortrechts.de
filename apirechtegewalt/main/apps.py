from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "apirechtegewalt.main"

    def ready(self):
        import apirechtegewalt.main.signals  # noqa
