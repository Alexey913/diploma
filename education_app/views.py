import logging
from typing import Callable

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.db.models.query import QuerySet

from abstract_app.views import  menu, check_authorization, get_data_with_verbose_name
from user_app.models import Data

from .models import Diploma
from .forms import DiplomaForm


logger = logging.getLogger(__name__)


def show_diploma(diploma_id: int) -> dict:
    diploma = Diploma.objects.filter(pk=diploma_id).first()
    if diploma:
        list_fields = ['name','number', 'series',
                       'date_registration', 'registration_number',
                       'name_institution', 'year_of_start_edu',
                       'year_of_finish_edu', 'spiciality',
                       'spicialization', 'description']
        dip_instance = Diploma.objects.values(*list_fields).filter(pk=diploma_id).first()
        object_dip = get_object_or_404(Diploma, pk=diploma_id)
        return get_data_with_verbose_name(object_dip, dip_instance)


def show_diplomas(diplomas: QuerySet) -> HttpResponse:
    if diplomas:
        output_diplomas = []
        for dip in output_diplomas:
            output_diplomas.append(show_diploma(dip.pk))
        return output_diplomas


@check_authorization
def education(request: HttpResponse, user_id: int) -> HttpResponse:
    diplomas = Diploma.objects.filter(user_id=user_id).all()
    if diplomas:
        context = {'diplomas': diplomas,
                   'title': 'Данные об образовании',
                   'user_id': user_id,
                   'user': Data.objects.filter(user_id=user_id).first(),
                   'menu': menu}
        return render(request, 'education_app/show_diplomas.html', context=context)
    logger.debug(f"Нет данных об образовании пользователя {user_id} - \
переход к заполнению данных")
    messages.error(request,
        'Нет сведений об образовании. Добавьте документ')
    return redirect('add_diploma', user_id=user_id)


@check_authorization
def show_diplomas_for_change(request: HttpResponse, user_id: int) -> HttpResponse:
    diplomas = Diploma.objects.filter(user_id=user_id).all()
    context = {'diplomas': diplomas,
               'user_id': user_id,
               'title': 'Документы об образовании',
               'user_name': Data.objects.filter(user_id=user_id).first(),
               'menu': menu}
    return render(request, 'education_app/show_diplomas.html', context=context)


@check_authorization
def get_diploma(request: HttpResponse,
                user_id: int, diploma_id: int) -> HttpResponse:
    diploma_dict = show_diploma(diploma_id)
    if diploma_dict:
        context = {'diploma_dict': diploma_dict,
                   'title': f'Данные об образовании',
                   'user_id': user_id,
                   'menu': menu,
                   'diploma': Diploma.objects.filter(pk=diploma_id).first()}
        return render(request, 'education_app/get_diploma.html', context=context)
    messages.error(request, "Необходимо заполнить данные")
    return redirect('change_diploma', user_id=user_id, diploma_id=diploma_id)


@check_authorization
def add_diploma(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        form = DiplomaForm(request.POST)
        if form.is_valid():
            diploma = form.save(commit=False)
            diploma.user_id = user_id
            diploma.save()
            messages.success(request, "Документ об образовании создан")
            logger.info(f"Сохранение данных об образовании пользователя {user_id}")
            return redirect('education', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных об образовательном документе пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = DiplomaForm()
    context = {'form': form,
               'title': 'Документ об образовании',
               'user_id': user_id,
               'menu': menu}
    return render(request, 'education_app/new_diploma.html', context=context)


@check_authorization
def change_diploma(request: HttpResponse, user_id: int, diploma_id: int) -> HttpResponse:
    current_diploma = Diploma.objects.filter(pk=diploma_id).first()
    if request.method == 'POST':
        form = DiplomaForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            for field, value in data_by_form.items():
                if value:
                    setattr(current_diploma, field, value)
            current_diploma.save()
            logger.info(f"Изменение данных о дипломе {diploma_id} пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('education', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных диплома {diploma_id} пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = DiplomaForm()
    context = {'form': form,
               'title': 'Изменение данных об образовании',
               'user_id': user_id,
               'diploma': current_diploma,
               'menu': menu}
    return render(request, 'education_app/edit_diploma.html', context)


@check_authorization
def del_diploma(request: HttpResponse, user_id: int, diploma_id: int) -> HttpResponse:
    try:
        Diploma.objects.filter(pk=diploma_id).delete()
        logger.info(f"Удалены данные об образовательном документе {diploma_id} {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных об образовательном документе {diploma_id} {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('education', user_id=user_id)
