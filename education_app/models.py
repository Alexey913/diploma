from django.db import models

from abstract_app.models import CommonDocTemplate

from user_app.models import User

from abstract_app.views import DIPLOMA_CATEGORIES


class DiplomaTemplate(CommonDocTemplate):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True


class Diploma(DiplomaTemplate):

    name = models.CharField(max_length=50,
                            default='Диплом',
                            choices=sorted(DIPLOMA_CATEGORIES),
                            verbose_name='Вид документа')
    registration_number = models.IntegerField(null=True,
                                              blank=True,
                                              verbose_name='Регистрационный номер')
    name_institution = models.CharField(max_length=100,
                                        verbose_name='Название учебного заведения')
    year_of_start_edu = models.IntegerField(null=True,
                                            blank=True,
                                            verbose_name='Год начала обучения')
    year_of_finish_edu = models.IntegerField(null=True,
                                            blank=True,
                                            verbose_name='Год окончания обучения')
    spiciality = models.CharField(max_length=100,
                                  null=True,
                                  blank=True,
                                  verbose_name='Специальность')
    spicialization = models.CharField(max_length=100,
                                      null=True,
                                      blank=True,
                                      verbose_name='Специализация')
    description = models.TextField(null=True, blank=True,
                                   verbose_name='Дополнительные сведения')

    class Meta:
        db_table = 'education_app_diploma'

    def __str__(self):
        return f'{self.name} № {self.series} {self.number}'