from django.db import models

from abstract_app.models import People, AbstractUser

class User(AbstractUser):

    def __str__(self):
        return f'{self.phone if self.phone else self.email}'
    
    class Meta:
        db_table = "user_app_user"


class Data(People):
    birth_place = models.CharField(max_length=100, null=True, blank=True, verbose_name='Место рождения')
    place_residense = models.CharField(max_length=100, null=True, blank=True, verbose_name='Место жительства')
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, primary_key=True)
    
    class Meta:
        db_table = "user_app_data"
