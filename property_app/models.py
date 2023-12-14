from django.db import models

from abstract_app.models import AbstractProperty

from user_app.models import User

from abstract_app.views import TRANSPORT_CATEGORIES, REALTY_CATEGORIES


class Property(AbstractProperty):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Transport(Property):
    type_property = models.CharField(max_length=12,
                                     default='Автомобиль',
                                     choices=sorted(TRANSPORT_CATEGORIES),
                                     verbose_name='Тип транспортного средства')
    brand = models.CharField(max_length=16,
                             verbose_name='Марка ТС')
    model = models.CharField(max_length=16,
                             verbose_name='Модель ТС')
    year_release = models.IntegerField(verbose_name='Год выпуска ТС')
    power_engine = models.IntegerField(null=True,
                                       blank=True,
                                       verbose_name='Мощность двигателя, л.с.')
    registration_number = models.CharField(max_length=9, null=True,
                                              blank=True,
                                              verbose_name='Регистрационный номер')
    weigth = models.IntegerField(null=True,
                                 blank=True,
                                 verbose_name='Масса ТС, кг')
    carrying = models.IntegerField(null=True,
                                   blank=True,
                                   verbose_name='Грузоподъемность ТС, кг')
    
    class Meta:
        db_table = 'property_app_transport'

    def __str__(self) -> str:
        return f'{self.type_property} {self.brand or ""} \
{self.model or ""} {self.registration_number or ""}'


class Realty(Property):
    type_property = models.CharField(max_length=20,
                                     default='Квартира',
                                    choices=sorted(REALTY_CATEGORIES),
                                    verbose_name='Тип недвижимости')
    cadastral_number = models.CharField(max_length=24,
                                        verbose_name='Кадастровый номер')
    cadastral_cost = models.DecimalField(max_digits=16, decimal_places=2,
                                         verbose_name='Кадастровая стоимость, руб.')
    adress = models.CharField(max_length=100, null=True, blank=True, verbose_name='Адрес объекта')
    area = models.DecimalField(max_digits=8, decimal_places=2,
                               verbose_name='Площадь, кв.м.')

    class Meta:
        db_table = 'property_app_realty'

    def __str__(self) -> str:
        return f'{self.type_property} {self.area} кв.м. {self.cadastral_number}'