from django.db import models

from abstract_app.models import DocTemplate, People

from user_app.models import User

from abstract_app.views import MILITARY_CATEGORIES



class Document(DocTemplate):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        abstract = True


class Spouce(People):
    date_marriage = models.DateField(
        null=True, blank=True, verbose_name='Дата регистрации брака')
    passport = models.OneToOneField(
        'Passport', on_delete=models.CASCADE, primary_key=True)

    class Meta:
        db_table = "doc_app_spouce"


class Children(People):
    passport = models.ManyToManyField('Passport')

    class Meta:
        db_table = "doc_app_children"


class Passport(Document):
    adress_registration = models.CharField(
        max_length=100, verbose_name='Адрес регистрации', null=True, blank=True)
    date_adress_reg = models.DateField(
        verbose_name='Дата регистрации', null=True, blank=True)
    adress_reg_eq_place = models.BooleanField(
        verbose_name='Совпадает с адресом проживания', default=False)

    class Meta:
        db_table = "doc_app_passport"


class Inn(Document):
    inn = models.IntegerField(verbose_name='ИНН')

    class Meta:
        db_table = "doc_app_inn"


class Snils(Document):

    class Meta():
        db_table = "doc_app_snils"


class DriverCategory(models.Model):
    name = models.CharField(max_length=3, verbose_name='Категория')
    description = models.CharField(
        max_length=60, verbose_name='Транспортное средстов')

    def __str__(self) -> str:
        return f'{self.name} - {self.description}'

    class Meta:
        db_table = "doc_app_driver_category"


class DriverLicense(Document):

    date_end_action = models.DateField(verbose_name='Окончание действия')
    date_start_expirience = models.DateField(
        verbose_name='Начало стажа', null=True, blank=True)
    special_marks = models.CharField(
        max_length=40, null=True, blank=True, verbose_name='Особые отметки')
    categories = models.ManyToManyField(
        'DriverCategory', blank=True, through='DriverCategoryShedule',
        verbose_name='Разрешенные категории')

    class Meta:
        db_table = "doc_app_driver_license"


class DriverCategoryShedule(models.Model):
    driver_license = models.ForeignKey(
        DriverLicense, on_delete=models.CASCADE, verbose_name='ВУ')
    category = models.ForeignKey(
        DriverCategory, on_delete=models.CASCADE, verbose_name='Категория')
    date_begin = models.DateField(
        null=True, default=None, verbose_name='Начало действия')
    date_end = models.DateField(
        null=True, default=None, verbose_name='Окончание действия')
    note = models.CharField(max_length=5, null=True,
                            blank=True, verbose_name='Отметка о категории')

    class Meta:
        db_table = "doc_app_driver_category_shedule"


class ForeignPassport(Document):
    foreign_name = models.CharField(
        max_length=50, verbose_name='Имя латиницей')
    foreign_surname = models.CharField(
        max_length=50, verbose_name='фамилия латиницей')
    date_end_action = models.DateField(verbose_name='Дата окончания')

    class Meta:
        db_table = "doc_app_foreign_pass"


class MilitaryTicket(Document):
    category = models.CharField(max_length=40, choices=sorted(
        MILITARY_CATEGORIES), verbose_name='Призывная категория')
    speciality = models.CharField(max_length=50, blank=True, null=True,
                                  verbose_name='Военная специальность')
    description = models.TextField(blank=True, null=True,
                                   verbose_name='Дополнительные сведения')

    class Meta:
        db_table = "doc_app_military_ticket"
