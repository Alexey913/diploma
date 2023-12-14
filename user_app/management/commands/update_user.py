from django.core.management.base import BaseCommand
from user_app.models import User


class Command(BaseCommand):
    help = "Update user name by id."

    def add_arguments(self, parser):
        parser.add_argument('pk', type=int, help='User ID')
        parser.add_argument('place_residense', type=str, help='User adress')

    def handle(self, *args, **kwargs):
        pk = kwargs.get('pk')
        adress = kwargs.get('place_residense')
        user = User.objects.filter(pk=pk).first()
        user.place_residense = adress
        user.save()
        self.stdout.write(f'{user.place_residense}')
