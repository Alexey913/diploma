import logging
from typing import Callable
from django import forms

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.db import models

from abstract_app.views import properties, menu, check_authorization, get_data_with_verbose_name
from user_app.models import Data

from .models import Transport, Realty
from .forms import TransportForm, RealtyForm


logger = logging.getLogger(__name__)


@check_authorization
def get_properties(request: HttpResponse, user_id: int) -> HttpResponse:
    context = {'title': 'Собственность пользователя',
               'user_id': user_id,
               'properties': properties,
               'menu': menu}
    return render(request, 'property_app/property.html', context=context)


def show_list_property(request: HttpResponse, user_id: int, kind: str,
                       entity: models.Model, title: str) -> HttpResponse:
    properties = entity.objects.filter(user_id=user_id).all()
    if properties:
        context = {'title': title,
                   'user_id': user_id,
                   'properties': properties,
                   'menu': menu,
                   'user': Data.objects.filter(user_id=user_id).first(),
                   'add_property': 'add_'+kind,
                   'get_property': 'get_'+kind}
        return render(request, 'property_app/show_list_property.html', context=context)
    logger.debug(f"Нет данных по разделу {title} пользователя {user_id} - \
# переход к добавлению объекта в {title}")
    messages.error(request, f'Раздел {title} пуст. Добавьте {title}')
    if kind == 'transport':
        return add_transport(request, user_id)
    return add_realty(request, user_id)
    

@check_authorization
def show_list_realty(request: HttpResponse, user_id: int) -> HttpResponse:
    return show_list_property(request, user_id, 'realty', Realty, 'Недвижимость')


@check_authorization
def show_list_transport(request: HttpResponse, user_id: int) -> HttpResponse:
    return show_list_property(request, user_id, 'transport', Transport,
                              'Транспорт')


@check_authorization
def add_property(request: HttpResponse, user_id: int,
                 type_form: forms.ModelForm,
                 in_title: str, kind: str) -> HttpResponse:
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.user_id = user_id
            prop.save()
            messages.success(request, f"Успешное создание {in_title}")
            logger.info(f"Сохранение {in_title} пользователя {user_id}")
            return redirect(kind, user_id=user_id)
        logger.debug(
            f"Ошибка сохранения {in_title} пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = type_form()
    context = {'form': form,
               'title': 'Добавление '+in_title,
               'add_property': 'add_'+kind,
               'user_id': user_id,
               'menu': menu}
    return render(request, 'property_app/new_property.html', context=context)


@check_authorization
def add_transport(request: HttpResponse, user_id: int) -> Callable:
    return add_property(request, user_id, TransportForm,
                 'транспортного средства', 'transport')


@check_authorization
def add_realty(request: HttpResponse, user_id: int) -> Callable:
    return add_property(request, user_id, RealtyForm,
                 'объекта недвижимости', 'realty')


def show_property(property_id: int, entity: models.Model, list_fields: list) -> dict:
    properties = entity.objects.filter(pk=property_id).first()
    if properties:
        prop_instance = entity.objects.values(*list_fields).filter(pk=property_id).first()
        object_property = get_object_or_404(entity, pk=property_id)
        return get_data_with_verbose_name(object_property, prop_instance)


def get_property(request: HttpResponse, user_id: int, property_id: int,
                 entity: models.Model, list_fields: list,
                 kind: str, in_title: str) -> HttpResponse:
    property_dict = show_property(property_id, entity, list_fields)
    if property_dict:
        context = {'properties': property_dict,
                   'title': f'Данные о {in_title}',
                   'user_id': user_id, 'menu': menu,
                   'add_property':'add_'+kind,
                   'change_property': 'change_'+kind,
                   'del_property': 'del_'+kind,
                   'property_id': property_id,
                   'property_name': entity.objects.filter(pk=property_id).first()}
        return render(request, 'property_app/get_property.html', context=context)
    messages.error(request, "необходимо заполнить данные")
    return redirect('change_'+kind, user_id=user_id, property_id=property_id)


@check_authorization
def get_realty(request:HttpResponse, user_id: int, property_id: int) -> Callable:
    list_fields = ['type_property', 'cadastral_number', 'cadastral_cost',
                   'adress', 'area', 'date_registration', 'description']
    return get_property(request, user_id, property_id, Realty, list_fields, 'realty', "недвижимости")


@check_authorization
def get_transport(request:HttpResponse, user_id: int, property_id: int) -> Callable:
    list_fields = ['type_property', 'brand', 'model', 'year_release',
                   'power_engine', 'registration_number', 'weigth',
                   'carrying', 'date_registration', 'description',]
    return get_property(request, user_id, property_id, Transport, list_fields, 'transport', "транспорте")


def change_property(request: HttpResponse, user_id: int, property_id: int,
                    type_form: forms.ModelForm, entity: models.Model,
                    kind:str, in_title: str) -> HttpResponse:
    current_property = entity.objects.filter(pk=property_id).first()
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            for field, value in data_by_form.items():
                if value:
                    setattr(current_property, field, value)
            current_property.save()
            logger.info(f"Изменение данных о {in_title} {property_id} \
пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('get_'+kind, user_id=user_id, property_id=property_id)
        logger.debug(
            f"Ошибка сохранения данных о {in_title} {property_id} \
пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = type_form()
    context = {'form': form,
               'title': f'Изменение данных о {in_title}',
               'user_id': user_id,
               'property_id': property_id,
               'change_property': 'change_'+kind,
               'del_property': 'del_'+kind,
               'property': current_property,
               'menu': menu}
    return render(request, 'property_app/edit_property.html', context)


@check_authorization
def change_transport(request: HttpResponse, user_id: int, property_id: int) -> Callable:
    return change_property(request, user_id, property_id,
                           TransportForm, Transport, 'transport',
                           'транспортном средстве')


@check_authorization
def change_realty(request: HttpResponse, user_id: int, property_id: int) -> Callable:
    return change_property(request, user_id, property_id,
                           RealtyForm, Realty, 'realty',
                           'объекте недвижимости')


def del_property(request: HttpResponse, user_id: int, property_id: int,
                 entity: models.Model, in_title: str, kind: str) -> HttpResponse:
    try:
        entity.objects.filter(pk=property_id).delete()
        logger.info(f"Удалены данные о {in_title} {property_id} \
пользователя {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных о {in_title} {property_id} \
пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect(kind, user_id=user_id)

@check_authorization
def del_realty(request: HttpResponse, user_id: int,
               property_id: int) -> HttpResponse:
    return del_property(request, user_id, property_id, Realty,
                        'объекте недвижимости', 'realty')


@check_authorization
def del_transport(request: HttpResponse, user_id: int,
              property_id: int) -> HttpResponse:
    return del_property(request, user_id, property_id, Transport,
                        'транспортном средстве', 'transport')