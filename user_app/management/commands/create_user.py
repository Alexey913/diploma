from django.core.management.base import BaseCommand

from user_app.models import User


class Command(BaseCommand):
    help = "Create user."

    def handle(self, *args, **kwargs):
        user = User(name='Иван', surname='Иванов',
                    email='mail@mail.ru', hash_password=8909876543)
        user.save()
        self.stdout.write(f'{user}')
