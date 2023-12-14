from django.db import models
from user_app.models import User


class Phone(models.Model):
    phone = models.IntegerField(blank=True, verbose_name='Номер телефона')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.phone}'


class Email(models.Model):
    email = models.EmailField(blank=True, verbose_name='E-mail')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.email}'
    

class Contact(models.Model):
    surname = models.CharField(max_length=50, null=True, 
                               blank=True, verbose_name='Фамилия')
    name = models.CharField(max_length=50, null=True,
                            blank=True, verbose_name='Имя')
    patronymic = models.CharField(max_length=50, null=True,
                                  blank=True, verbose_name='Отчество')
    organization = models.CharField(max_length=50, null=True,
                                    blank=True, verbose_name='Организация')
    birthday = models.DateField(blank=True, null=True, verbose_name='День рождения')
    place_residense = models.DateField(blank=True, null=True, verbose_name='Адрес')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    
    def __str__(self) -> str:
        return f'{self.surname + " " + self.name if self.surname and self.name else self.surname or self.name}'
