from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "web.apps.core"
    label = "core"
    verbose_name = "병원 AI"
    default_auto_field = "django.db.models.BigAutoField"
