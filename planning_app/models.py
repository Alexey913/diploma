from django.db import models
from django.utils.timezone import now

from user_app.models import User

from abstract_app.views import REPEAT_LIST


class Remind(models.Model):
    title = models.CharField(max_length=20, verbose_name='Заголовок', default=f'Напоминание')
    date = models.DateField(verbose_name='Дата', default=now)
    time = models.TimeField(verbose_name='Время', default=now)
    all_day = models.BooleanField(verbose_name='Весь день', default=False)
    repeat = models.CharField(max_length=20, choices=sorted(REPEAT_LIST),
                              verbose_name='Повтор', default='Никогда')
    description = models.TextField(null=True, blank=True, verbose_name='Описание события')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repeat_id = models.IntegerField(null=True)

def __str__(self):
    return f'{self.name} {self.date}'