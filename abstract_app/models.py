from django.db import models

from .views import GENDERS

class AbstractUser(models.Model):

    class Meta:
        abstract = True

    email = models.EmailField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    hash_password = models.BinaryField()
    salt = models.BinaryField()


class People(models.Model):

    class Meta:
        abstract = True

    surname = models.CharField(
        max_length=50, null=True, blank=True, verbose_name='Фамилия')
    name = models.CharField(max_length=50, null=True,
                            blank=True, verbose_name='Имя')
    patronymic = models.CharField(
        max_length=50, null=True, blank=True, verbose_name='Отчество')
    birthday = models.DateField(
        null=True, blank=True, verbose_name='Дата рождения')
    gender = models.CharField(max_length=7, null=True,
                              blank=True, choices=GENDERS, verbose_name='Пол')
    
    def __str__(self) -> str:
        return f'{self.surname or ""} {self.name or ""} {self.patronymic or ""}'


class CommonDocTemplate(models.Model):

    class Meta:
        abstract = True

    series = models.CharField(max_length=10, null=True, verbose_name='Серия')
    number = models.IntegerField(verbose_name='Номер')
    date_registration = models.DateField(verbose_name='Дата выдачи')

class DocTemplate(CommonDocTemplate):

    class Meta:
        abstract = True

    id_inspection = models.IntegerField(
        null=True, blank=True, verbose_name='Код подразделения')
    name_inspection = models.CharField(
        max_length=50, null=True, blank=True, verbose_name='Название подразделения')
    

class AbstractProperty(models.Model):

    class Meta:
        abstract = True

    date_registration = models.DateField(verbose_name='Дата постановки на учет')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')