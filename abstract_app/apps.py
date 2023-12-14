from django.apps import AppConfig


class AbstractAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abstract_app'
