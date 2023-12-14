from typing import Callable
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages

from abstract_app.views import  menu, check_authorization, get_data_with_verbose_name

from django.db.models.query import QuerySet

import locale

import logging

import numpy as np 

from calendar import HTMLCalendar
from datetime import datetime

from dateutil import rrule

from .models import Remind
from .forms import RemindForm, SearchRemindDateForm, SearchRemindTitleForm


locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)


logger = logging.getLogger(__name__)


def show_calendar() -> dict:
    now_time = datetime.now()
    year = now_time.year
    month = now_time.month
    date = now_time.strftime('%d, %B, %Y')
    time = now_time.strftime('%H:%M')
    calendar = HTMLCalendar().formatmonth(year, month)
    return {'calendar': calendar,
            'date': date,
            'time': time
            }


def get_reminds(request: HttpResponse, user_id: int,
                reminds: QuerySet,mes: str, title: str) -> HttpResponse:
    context = {'date_dict': show_calendar(),
               'user_id': user_id,
               'reminds': reminds,
               'title': title,
               'mes': mes,
               'menu': menu}
    return render(request, 'planning_app/reminds.html', context=context)


@check_authorization
def reminds(request: HttpResponse, user_id: int) -> Callable:
    today = datetime.today() 
    reminds = Remind.objects.filter(user_id=user_id,
                                    date__year=today.year,
                                    date__month=today.month,
                                    date__day=today.day).all()
    mes = 'На сегодня событый нет'
    title = 'События на сегодня'
    return get_reminds(request, user_id, reminds, mes, title)
   

@check_authorization
def reminds_at_current_month(request: HttpResponse, user_id: int) -> Callable:
    today = datetime.today()
    reminds = Remind.objects.filter(user_id=user_id,
                                    date__year=today.year,
                                    date__month=today.month).all()
    mes = 'В текущем месяце нет событий'
    title = 'События в текущем  месяце'
    return get_reminds(request, user_id, reminds, mes, title)


def func_for_add_repeat_events(remind:Remind, func: Callable, delta: int, period: str):
    end_date_year = int(str(np.datetime64(str(datetime.now().year)) + np.timedelta64(100,'Y')))
    current_day = remind.date
    end_date=datetime(year=end_date_year-delta, month=1, day=1)
    for dt in rrule.rrule(func, dtstart=current_day, until=end_date):
            Remind.objects.create(title=remind.title,
                                        date=dt, time=remind.time,
                                        all_day=remind.all_day,
                                        repeat=period,
                                        description=remind.description,
                                        user = remind.user,
                                        repeat_id=remind.pk)


def add_event_with_repeat(remind:Remind):
    if remind.repeat == 'Каждый день':
        func_for_add_repeat_events(remind, rrule.DAILY, 98, 'Каждый день')
    elif remind.repeat == 'Каждую неделю':
        func_for_add_repeat_events(remind, rrule.WEEKLY, 95, 'Каждую неделю')
    elif remind.repeat == 'Каждый месяц':
        func_for_add_repeat_events(remind, rrule.MONTHLY, 80, 'Каждый месяц')
    elif remind.repeat == 'Каждый год':
        func_for_add_repeat_events(remind, rrule.YEARLY, 0, 'Каждый год')


def get_dict_remind(remind_id: int) -> Callable:
    remind = Remind.objects.values('title', 'date','time', 'repeat',
                                           'description').filter(
                                               pk=remind_id).first()
    object_remind = get_object_or_404(Remind, pk=remind_id)
    if object_remind.all_day:
        remind['time'] = 'Целый день'
    return get_data_with_verbose_name(object_remind, remind)


@check_authorization
def add_remind(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        form = RemindForm(request.POST)
        if form.is_valid():
            remind = form.save(commit=False)
            remind.user_id = user_id
            if remind.all_day == True:
                remind.time = '00:00:00'
            remind.save()
            remind.repeat_id = remind.pk
            remind.save()
            add_event_with_repeat(remind)
            messages.success(request, "Создано новое событие")
            logger.info(f"Сохранение данных о событии пользователя {user_id}")
            return redirect('show_remind', user_id=user_id, remind_id=remind.pk)
        logger.debug(f"Ошибка сохранения события пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = RemindForm()
    context = {'date_dict': show_calendar(),
               'form': form,
               'title': 'Добавить событие',
               'user_id': user_id,
               'menu': menu}
    return render(request, 'planning_app/new_remind.html', context=context)


@check_authorization
def change_remind(request: HttpResponse, user_id: int, remind_id: int) -> HttpResponse:
    current_remind = Remind.objects.filter(pk=remind_id).first()
    dict_remind = get_dict_remind(remind_id)
    if request.method == 'POST':
        form = RemindForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            for field, value in data_by_form.items():
                if value and field != 'all_day' and field != 'time':
                    setattr(current_remind, field, value)
            if data_by_form['all_day']:
                current_remind.time = '00:00:00'
            else:
                current_remind.time = data_by_form['time'] or current_remind.time
            current_remind.save()
            Remind.objects.filter(repeat_id=current_remind.repeat_id).exclude(
                pk=current_remind.pk).all().delete()
            add_event_with_repeat(current_remind)
            messages.success(request, "Событие изменено")
            logger.info(f"Сохранение данных о событии пользователя {user_id}")
            return redirect('show_remind', user_id=user_id, remind_id=remind_id)
        logger.debug(f"Ошибка сохранения события пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = RemindForm()
    context = {'date_dict': show_calendar(),
               'form': form,
               'title': 'Изменить событие',
               'user_id': user_id,
               'remind_id': remind_id,
               'remind': dict_remind,
               'menu': menu}
    return render(request, 'planning_app/edit_remind.html', context=context)


@check_authorization
def show_remind(request: HttpResponse, user_id: int, remind_id: int) -> HttpResponse:
    current_remind = get_dict_remind(remind_id)
    context = {'date_dict': show_calendar(),
               'remind': current_remind,
               'title': current_remind["Заголовок"],
               'user_id': user_id,
               'remind_id': remind_id,
               'menu': menu}
    return render(request, 'planning_app/show_remind.html', context=context)


@check_authorization
def del_remind(request: HttpResponse, user_id: int, remind_id: int) -> HttpResponse:
    try:
        current_remind = Remind.objects.filter(pk=remind_id).first()
        repeat_id = current_remind.repeat_id
        current_remind.delete()
        Remind.objects.filter(repeat_id=repeat_id).all().delete()
        logger.info(f"Удалено напоминание {remind_id} пользователя {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(f"Ошибка удаления напомиинания пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('reminds', user_id=user_id)
    
def inject_form(request) -> dict:
    return {"form_title":SearchRemindTitleForm(),
            "form_date":SearchRemindDateForm()}

@check_authorization
def search_by_title(request: HttpResponse, user_id: int) -> Callable:
    if request.method == 'POST':
        form = SearchRemindTitleForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            title = data_by_form['title']
            reminds = Remind.objects.filter(
                user_id=user_id, title__icontains=title).all()
            mes = 'По Вашему запросу ничего не найдено'
            title_templ = f'Найдено по названию {title}:'
            return get_reminds(request, user_id, reminds, mes, title_templ)
    else:
        form = SearchRemindTitleForm()
        reminds = None
    return redirect('search_by_title', user_id=user_id)

@check_authorization
def search_by_date(request: HttpResponse, user_id: int) -> Callable:
    if request.method == 'POST':
        form = SearchRemindDateForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            start_date = data_by_form['start_date']
            end_date = data_by_form['end_date']
            reminds = Remind.objects.filter(
                user_id=user_id, date__range=[start_date, end_date]).all()
            mes = 'По Вашему запросу ничего не найдено'
            title_templ = f'Найдено с {start_date} по {end_date}:'
            return get_reminds(request, user_id, reminds, mes, title_templ)
    else:
        form = SearchRemindDateForm()
        reminds = None
    return redirect('search_by_date', user_id=user_id)