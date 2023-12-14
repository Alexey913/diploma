from django.core.management.base import BaseCommand

from user_app.models import Data


class Command(BaseCommand):
    help = "Create user."

    def handle(self, *args, **kwargs):
        data = Data(name='Иван', surname='Иванов', patronymic='Иванович',
                    birthday='2020-10-10', place_residense='Москва',
                    birth_place='2020-10-10', gender='M', user_id=51)
        data.save()
        self.stdout.write(f'{data}')
