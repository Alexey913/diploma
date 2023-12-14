from django.core.management.base import BaseCommand

from planning_app.models import Remind


class Command(BaseCommand):
    help = "Delete database 'remind'"

    def handle(self, *args, **kwargs):
        Remind.objects.all().delete()
