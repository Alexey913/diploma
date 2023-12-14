from django.core.management.base import BaseCommand

from doc_app.models import DriverCategory
from abstract_app.views import DRIVER_CATEGORIES


class Command(BaseCommand):
    help = "Fill database 'driver_category'"

    def handle(self, *args, **kwargs):
        for cat, des in DRIVER_CATEGORIES.items():
            category = DriverCategory(name=cat, description=des)
            category.save()
            self.stdout.write(f'{category}')
