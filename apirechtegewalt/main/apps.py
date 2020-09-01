from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "apirechtegewalt.main"

    def ready(self):
        import apirechtegewalt.main.signals  # noqa

        from watson import search as watson

        Incident = self.get_model("Incident")
        watson.register(Incident)
