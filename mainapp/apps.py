from django.apps import AppConfig
from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'
    verbose_name = 'Справочники'

