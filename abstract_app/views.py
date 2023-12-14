from django.http import Http404, HttpResponseNotFound
from django.shortcuts import redirect, HttpResponse
from django.contrib import messages
from django.db import models

from typing import Callable


import logging


logger = logging.getLogger(__name__)


GENDERS = (
    ('Мужской', 'Мужской'),
    ('Женский', 'Женский'),
)


DRIVER_CATEGORIES = {
    'A': 'Мотоциклы',
    'A1': 'Легковые мотоциклы',
    'B': 'Легковые автомобили, небольшиегрузовики (до 3,5 тонн)',
    'B1': 'Трициклы, квадрициклы',
    'C': 'Грузовые автомобили от 3,5 тонн',
    'C1': 'Средние грузовики (от 3,5 до 7,5 тонн)',
    'D': 'Автобусы',
    'D1': 'Небольшие автобусы',
    'BE': 'Легковые автомобили с прицепом',
    'CE': 'Грузовые автомобили с прицепом',
    'C1E': 'Средние грузовики с прицепом',
    'DE': 'Автобусы с пицепом',
    'D1E': 'Небольшие автобусы с прицепом',
    'M': 'Мопеды',
    'Tm': 'Трамваи',
    'Tb': 'Троллейбусы',
}


MILITARY_CATEGORIES = {
    ('A', 'А - Годен'),
    ('B', 'Б - Годен с небольшими ограничениями'),
    ('C', 'В - Ограниченно годен'),
    ('D', 'Г - Временно не годен'),
    ('E', 'Д - Не годен'),
}


DIPLOMA_CATEGORIES = {
    ('Диплом', 'Диплом'),
    ('Аттестат', 'Аттестат'),
    ('Свидетельство', 'Свидетельство'),
    ('Сертификат', 'Сертификат'),
}


TRANSPORT_CATEGORIES = {
    ('Автомобиль', 'Автомобиль'),
    ('Мотоцикл', 'Мотоцикл'),
    ('Квадроцикл', 'Квадроцикл'),
    ('Трицикл', 'Трицикл'),
    ('Трактор', 'Трактор'),
    ('Автобус', 'Автобус'),
    ('Вертолет', 'Вертолет'),
    ('Самолет', 'Самолет'),
    ('Катер', 'Катер'),
    ('Прицеп', 'Прицеп'),
}


REALTY_CATEGORIES = {
    ('Квартира', 'Квартира'),
    ('Дом', 'Дом'),
    ('Земельный участок', 'Земельный участок'),
    ('Гараж', 'Гараж'),
    ('Складское помещений', 'Складское помещение'),
}


REPEAT_LIST = {
    ('Никогда', 'Никогда'),
    ('Каждый день', 'Каждый день'),
    ('Каждую неделю', 'Каждую неделю'),
    ('Каждый месяц', 'Каждый месяц'),
    ('Каждый год', 'Каждый год'),
}


def redirect_with_error(request: HttpResponse) -> Exception:
    if not 'pk' in request.session:
        logger.debug(f"Попытка неавторизованного входа")
        messages.error(request, 'Для работы с офисом необходимо авторизоваться')
        return redirect('authorization')
    raise Http404


def check_authorization(func: Callable) -> Callable:
    def wrapper(request: HttpResponse, user_id: int, *args, **kwargs):
        if 'pk' in request.session and request.session['pk'] == user_id:
            return func(request, user_id, *args, **kwargs)
        return redirect_with_error(request)
    return wrapper


def check_doc(entity: models.Model, redirect_func: str) -> Callable:
    def deco(func: Callable) -> Callable:
        def wrapper(request, user_id: int, *args, **kwargs) -> HttpResponse:
            if entity.objects.filter(user_id=user_id).first():
                return func(request, user_id, *args, **kwargs)
            logger.debug(
                f"Документа пользователя {user_id} не существует, redirect to {redirect_func}")
            messages.error(
                request, 'Для работы с документом необходимо ввести его данные')
            return redirect(redirect_func, user_id=user_id)
        return wrapper
    return deco


def pageNotFound(request: HttpResponse, exception: Exception) -> HttpResponseNotFound:
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def get_data_with_verbose_name(the_object:object, dict_data: dict) -> dict:
    output = {}
    for name_field, value in dict_data.items():
        if value != None:
            output[the_object._meta.get_field(name_field).verbose_name] = dict_data[name_field]
    return output


menu = [{'title': 'Личные данные', 'url_name': 'data'},
        {'title': 'Документы', 'url_name': 'docs'},
        {'title': 'Собственность', 'url_name': 'properties'},
        {'title': 'Образование', 'url_name': 'education'},
        {'title': 'Планировщик', 'url_name': 'reminds'},
        {'title': 'Контакты', 'url_name': 'contacts'},
        ]


documents = [
    {'title': 'Паспорт', 'url_name': 'passport'},
    {'title': 'ИНН', 'url_name': 'inn'},
    {'title': 'СНИЛС', 'url_name': 'snils'},
    {'title': 'Водительское удостоверение', 'url_name': 'driver_license'},
    {'title': 'Заграничный паспорт', 'url_name': 'foreign_passport'},
    {'title': 'Военный билет', 'url_name': 'military_ticket'},
]


properties = [
    {'title': 'Недвижимость', 'url_name': 'realty'},
    {'title': 'Транспорт', 'url_name': 'transport'},
]