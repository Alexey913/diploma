import logging
from typing import Callable
from django import forms

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.db import models

from abstract_app.views import documents, menu, check_authorization, \
    check_doc, get_data_with_verbose_name

from .models import Children, DriverCategory, Passport, Inn, \
    Snils, DriverLicense, MilitaryTicket, \
    ForeignPassport, Spouce, People, DriverCategoryShedule, Document

from .forms import PassportForm, InnForm, DriverLicenseForm, \
    ForeignPassportForm, MilitaryTicketForm, \
    SnilsForm, SpouceForm, ChildrenForm, \
    DriverCategoryAddForm, DriverCategoryEditForm

from user_app.models import Data


logger = logging.getLogger(__name__)


def load_form_people(entity: People, data_by_form: type):
    entity.name = data_by_form['name'] or entity.name
    entity.surname = data_by_form['surname'] or entity.surname
    entity.patronymic = data_by_form['patronymic'] or entity.patronymic
    entity.birthday = data_by_form['birthday'] or entity.birthday
    entity.gender = data_by_form['gender'] or entity.gender
    entity.save()

def get_user_by_id(user_id:int) -> Data:
    return Data.objects.filter(user_id=user_id).first()


@check_authorization
def docs(request: HttpResponse, user_id: int) -> HttpResponse:
    context = {'title': 'Документы',
               'user_id': user_id,
               'documents': documents,
               'user': get_user_by_id(user_id),
               'menu': menu}
    return render(request, 'doc_app/docs.html', context=context)


def get_document(entity: models.Model, user_id: int, list_fields: list) -> dict:
    data = Data.objects.values('surname', 'name', 'patronymic',
                               'birthday', 'birth_place',
                               'gender').filter(
        user_id=user_id).first()
    entity_instance = entity.objects.values(
        *list_fields).filter(user_id=user_id).first()
    object_data = get_object_or_404(Data, user_id=user_id)
    object_entity = get_object_or_404(entity, user_id=user_id)
    return {**get_data_with_verbose_name(object_data, data),
            **get_data_with_verbose_name(object_entity, entity_instance)}


def show_spouce(passport: Passport) -> dict:
    if passport and Spouce.objects.filter(pk=passport.pk):
        spouce = Spouce.objects.values('surname', 'name', 'patronymic',
                                       'birthday', 'gender',
                                       'date_marriage').filter(
            pk=passport.pk).first()
        object_spouce = get_object_or_404(Spouce, pk=passport.pk)
        return get_data_with_verbose_name(object_spouce, spouce)


def show_childrens(passport: Passport) -> list[dict]:
    if passport:
        childrens = Passport.objects.filter(
            pk=passport.pk).first().children_set.all()
        output_cilds = []
        for child in childrens:
            children = Children.objects.values('surname', 'name',
                                               'patronymic', 'birthday',
                                               'gender').filter(
                                                   pk=child.pk).first()
            object_child = get_object_or_404(Children, pk=child.pk)
            output_cilds.append(
                get_data_with_verbose_name(object_child, children))
        return output_cilds


@check_doc(Passport, 'change_passport')
@check_authorization
def get_passport(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['series', 'number', 'date_registration',
                   'id_inspection', 'name_inspection',
                   'adress_registration', 'date_adress_reg']
    object_passport = get_object_or_404(Passport, user_id=user_id)
    spouce = show_spouce(object_passport)
    childrens = show_childrens(object_passport)
    context = get_document(Passport, user_id, list_fields)
    context_to_template = {'context': context,
                           'spouce': spouce,
                           'childrens': childrens,
                           'title': 'Паспорт',
                           'user_id': user_id,
                           'user': get_user_by_id(user_id),
                           'view': 'change_passport',
                           'menu': menu}
    return render(request, 'doc_app/passport.html', context=context_to_template)


@check_authorization
def change_passport(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        form = PassportForm(request.POST)
        if form.is_valid():
            current_passport = Passport.objects.filter(
                user_id=user_id).first()
            if current_passport:
                data_by_form = form.cleaned_data
                for field, value in data_by_form.items():
                    if value and field != 'adress_registration':
                        setattr(current_passport, field, value)
                if current_passport.adress_reg_eq_place:
                    current_passport.adress_registration = \
                        get_user_by_id(user_id).place_residense
                else:
                    current_passport.adress_registration = \
                        data_by_form['adress_registration'] \
                        or current_passport.adress_registration
                current_passport.save()
            else:
                passport = form.save(commit=False)
                passport.user_id = user_id
                passport.save()
            messages.success(request, "Паспортные данные успешно изменены")
            logger.info(f"Сохранение паспортных данных пользователя {user_id}")
            return redirect('passport', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения паспортных данных пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = PassportForm()
    context = {'form': form,
               'title': 'Изменение паспортных данных',
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'menu': menu}
    return render(request, 'doc_app/change_passport.html', context=context)


@check_authorization
def add_people(request: HttpResponse, user_id: int, kind: str,
               type_form: forms.ModelForm, in_title: str) -> HttpResponse:
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid() and form.has_changed():
            people = form.save(commit=False)
            people.passport_id = user_id
            people.save()
            if kind == 'edit_spouce':
                Passport.objects.filter(
                user_id=user_id).first().spouce = people
            else:
                Passport.objects.filter(
                    user_id=user_id).first().children_set.add(people)
            logger.info(
                f"Сохранение данных о {in_title} пользователя {user_id}")
            messages.success(request, f"Данные о {in_title} добавлены")
            return redirect('passport', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных о {in_title} пользователя {user_id}")
        messages.error(request, "Необходимо заполнить хотя бы одно поле")
    else:
        form = type_form()
    context = {'form': form,
               'title': 'Данные о супруге',
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'menu': menu}
    return render(request, f'doc_app/{kind}.html', context)


@check_authorization
def add_spouce(request: HttpResponse, user_id: int) -> Callable:
    return add_people(request, user_id, 'edit_spouce', SpouceForm, 'супруге')


@check_authorization
def add_children(request: HttpResponse, user_id: int) -> Callable:
    return add_people(request, user_id, 'new_children', ChildrenForm, 'детях')


@check_authorization
def change_spouce(request: HttpResponse, user_id: int) -> HttpResponse:
    current_spouce = Spouce.objects.get(passport_id=user_id)
    if request.method == 'POST':
        form = SpouceForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            load_form_people(current_spouce, data_by_form)
            current_spouce.date_marriage = data_by_form['date_marriage']\
                or current_spouce.date_marriage
            current_spouce.save()
            logger.info(f"Изменение данных о супруге пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('passport', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения паспортных данных пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = SpouceForm()
    context = {'form': form,
               'title': 'Данные о супруге',
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'spouce': current_spouce,
               'menu': menu}
    return render(request, 'doc_app/edit_spouce.html', context)


@check_authorization
def change_children(request: HttpResponse, user_id: int, children_id: int) -> HttpResponse:
    current_children = Children.objects.filter(pk=children_id).first()
    if request.method == 'POST':
        form = ChildrenForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            load_form_people(current_children, data_by_form)
            logger.info(f"Изменение данных о детях пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('show_children', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения паспортных данных пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = ChildrenForm()
    context = {'form': form,
               'title': 'Данные о детях',
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'children': current_children,
               'menu': menu}
    return render(request, 'doc_app/edit_children.html', context)


@check_doc(Passport, 'change_passport')
@check_authorization
def edit_spouce(request: HttpResponse, user_id: int) -> Callable:
    if Spouce.objects.filter(passport_id=user_id).first():
        return change_spouce(request, user_id)
    messages.debug(request, "Данные о супруге отсутствуют")
    return add_spouce(request, user_id)


@check_authorization
def show_childrens_for_change(request: HttpResponse, user_id: int) -> HttpResponse:
    childrens = Passport.objects.filter(pk=user_id).first().children_set.all()
    context = {'childrens': childrens,
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'menu': menu}
    return render(request, 'doc_app/show_children.html', context=context)


@check_doc(Passport, 'change_passport')
@check_authorization
def edit_children(request: HttpResponse, user_id: int) -> Callable:
    if not Passport.objects.filter(pk=user_id).first().children_set.all():
        messages.error(request, "Данные о детях отсутствуют")
        return add_children(request, user_id)
    return show_childrens_for_change(request, user_id)


@check_authorization
def del_spouce(request: HttpResponse, user_id: int) -> HttpResponse:
    try:
        Spouce.objects.filter(passport_id=user_id).delete()
        logger.info(f"Удалены данные о супруге пользователя {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных о супруге пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('passport', user_id=user_id)


@check_authorization
def del_children(request: HttpResponse, user_id: int, children_id: int) -> HttpResponse:
    try:
        Children.objects.filter(pk=children_id).delete()
        logger.info(f"Удалены данные о ребенке пользователя {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных о ребенке пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('passport', user_id=user_id)


@check_doc(Snils, 'change_snils')
@check_authorization
def get_snils(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['number', 'date_registration',
                   'id_inspection', 'name_inspection']
    context = get_document(Snils, user_id, list_fields)
    context_to_template = {'context': context,
                           'title': 'CНИЛС',
                           'user_id': user_id,
                           'user': get_user_by_id(user_id),
                           'view': 'change_snils',
                           'menu': menu}
    return render(request, 'doc_app/base_doc.html', context=context_to_template)


@check_doc(Inn, 'change_inn')
@check_authorization
def get_inn(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['inn', 'series', 'number',
                   'date_registration', 'id_inspection',
                   'name_inspection']
    context = get_document(Inn, user_id, list_fields)
    context_to_template = {'context': context,
                           'title': 'ИНН',
                           'user_id': user_id,
                           'view': 'change_inn',
                           'user': get_user_by_id(user_id),   
                           'menu': menu}
    return render(request, 'doc_app/base_doc.html', context=context_to_template)


@check_doc(ForeignPassport, 'change_foreign_passport')
@check_authorization
def get_foreign_passport(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['series', 'number', 'date_registration',
                   'id_inspection', 'name_inspection', 'foreign_name',
                   'foreign_surname', 'date_end_action']
    context = get_document(ForeignPassport, user_id, list_fields)
    context_to_template = {'context': context,
                           'title': 'Заграничный паспорт',
                           'view': 'change_foreign_passport',
                           'user_id': user_id,
                           'user': get_user_by_id(user_id),
                           'menu': menu}
    return render(request, 'doc_app/base_doc.html', context=context_to_template)


@check_doc(MilitaryTicket, 'change_military_ticket')
@check_authorization
def get_military_ticket(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['series', 'number', 'date_registration',
                   'id_inspection', 'name_inspection', 'category',
                   'speciality', 'description']
    context = get_document(MilitaryTicket, user_id, list_fields)
    context_to_template = {'context': context,
                           'title': 'Военный билет',
                           'view': 'change_military_ticket',
                           'user_id': user_id,   
                           'user': get_user_by_id(user_id),
                           'menu': menu}
    return render(request, 'doc_app/base_doc.html', context=context_to_template)


@check_authorization
def change_doc(request: HttpResponse, user_id: int, type_form: forms.ModelForm,
               entity: Document, title:str, kind: str, mes_error: str) -> HttpResponse:
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            current_doc = entity.objects.filter(
                user_id=user_id).first()
            if current_doc:
                data_by_form = form.cleaned_data
                for field, value in data_by_form.items():
                    if value:
                        setattr(current_doc, field, value)
                current_doc.save()
            else:
                doc = form.save(commit=False)
                doc.user_id = user_id
                doc.save()
            messages.success(request,
                             f"Данные документа {title} успешно изменены")
            logger.info(f"Сохранение {title} пользователя {user_id}")
            return redirect(kind, user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных {title} пользователя {user_id}")
        messages.error(request, mes_error)
    else:
        form = type_form()
    context = {'form': form,
               'title': f'Изменение документа {title}',
               'view': 'change_'+kind,
               'user_id': user_id,
      'user': get_user_by_id(user_id),
               'menu': menu}
    return render(request, 'doc_app/base_change_doc.html', context=context)


@check_authorization
def change_inn(request: HttpResponse, user_id: int) -> Callable:
    return change_doc(request, user_id, InnForm, Inn,
                      'ИНН', 'inn', 'Введите корректный номер ИНН')


@check_authorization
def change_snils(request: HttpResponse, user_id: int) -> Callable:
    return change_doc(request, user_id, SnilsForm, Snils,
                      'СНИЛС', 'snils', 'Введите корректный номер СНИЛС')


@check_authorization
def change_foreign_passport(request: HttpResponse, user_id: int) -> Callable:
    return change_doc(request, user_id, ForeignPassportForm, ForeignPassport,
                      'Заграничный паспорт', 'foreign_passport',
                      'Проверьте дату окончания действия или исправьте фамилию/имя на латиницу')


@check_authorization
def change_military_ticket(request: HttpResponse, user_id: int) -> Callable:
    return change_doc(request, user_id, MilitaryTicketForm, MilitaryTicket,
                      'Военный билет', 'military_ticket', 'Неверные данные')


@check_authorization
def add_driver_category(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        form = DriverCategoryAddForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.driver_license_id = user_id
            category.save()
            logger.info(
                f"Сохранение данных о водительской категории пользователя {user_id}")
            messages.success(request, "Данные о категории добавлены")
            return redirect('show_driver_categories', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных о категории {user_id}")
        messages.error(request, "Необходимо заполнить все поля")
    else:
        form = DriverCategoryAddForm()
    context = {'form': form,
               'title': 'Данные о категории',
               'user': get_user_by_id(user_id),
               'user_id': user_id,
               'menu': menu}
    return render(request, 'doc_app/new_driver_category.html', context)


@check_authorization
def del_driver_category(request: HttpResponse, user_id: int, category_id: int) -> HttpResponse:
    try:
        DriverCategoryShedule.objects.filter(
            driver_license_id=user_id, category_id=category_id).delete()
        logger.info(
            f"Удалены данные о категории {category_id} пользователя {user_id}")
        messages.success(request, "Данные успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных о категории {category_id} пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('driver_license', user_id=user_id)


@check_doc(DriverLicense, 'change_driver_license')
@check_authorization
def edit_driver_categories(request: HttpResponse, user_id: int) -> Callable:
    if not DriverLicense.objects.filter(pk=user_id).first().categories.all():
        messages.error(
            request, "Данные об открытых категориях отсутствуют")
        return change_driver_license(request, user_id)
    return show_categories_for_change(request, user_id)


@check_authorization
def change_driver_category(request: HttpResponse, user_id: int, category_id: int) -> HttpResponse:
    current_shedule_cat = DriverCategoryShedule.objects.filter(
        driver_license_id=user_id, category_id=category_id).first()
    if request.method == 'POST':
        form = DriverCategoryEditForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            for field, value in data_by_form.items():
                if value:
                    setattr(current_shedule_cat, field, value)
            current_shedule_cat.save()
            logger.info(
                f"Изменение данных о водительской категории {category_id} пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('show_driver_categories', user_id=user_id)
        logger.debug(f"Ошибка сохранения данных ВУ пользователя {user_id}")
        messages.error(request, "Неверные данные")
    else:
        form = DriverCategoryEditForm()
    context = {'form': form,
               'title':
               f'Категория {DriverCategory.objects.filter(pk=category_id).first().name}',
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'shedule_cat': current_shedule_cat,
               'menu': menu}
    return render(request, 'doc_app/edit_driver_cat.html', context)


@check_authorization
def show_categories_for_change(request: HttpResponse, user_id: int) -> HttpResponse:
    categories = DriverLicense.objects.filter(
        pk=user_id).first().categories.all().order_by('name')
    context = {'categories': categories,
               'user_id': user_id,
               'user': get_user_by_id(user_id),
               'title': 'Открытые категории',
               'menu': menu}
    return render(request, 'doc_app/show_driver_cat.html', context=context)


def show_driver_categories(driver_license: DriverLicense) -> list[dict]:
    if driver_license:
        categories = DriverCategoryShedule.objects.filter(
            driver_license_id=driver_license.pk).all()
        output_cats = []
        for cat in categories:
            category = DriverCategoryShedule.objects.values('category_id',
                                                            'date_begin',
                                                            'date_end',
                                                            'note').filter(
                                                                pk=cat.pk).first()
            object_category = get_object_or_404(DriverCategoryShedule, pk=cat.pk)
            temp = get_data_with_verbose_name(object_category, category)
            print(temp)
            temp['Категория'] = DriverCategory.objects.get(
                id=temp['Категория'])
            output_cats.append(temp)
        return output_cats


@check_doc(DriverLicense, 'change_driver_license')
@check_authorization
def get_driver_license(request: HttpResponse, user_id: int) -> HttpResponse:
    list_fields = ['series', 'number', 'date_registration',
                   'id_inspection', 'name_inspection', 'date_end_action',
                   'date_start_expirience', 'special_marks', 'categories']
    context = get_document(DriverLicense, user_id, list_fields)
    object_license = get_object_or_404(DriverLicense, user_id=user_id)
    categories = show_driver_categories(object_license)
    context_to_template = {'context': context,
                           'categories': categories,
                           'title': 'Водительское удостоверение',
                           'view': 'change_driver_license',
                           'user_id': user_id,
                           'user': get_user_by_id(user_id),
                           'menu': menu}
    return render(request, 'doc_app/driver_license.html', context=context_to_template)


@check_authorization
def change_driver_license(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        form = DriverLicenseForm(request.POST)
        if form.is_valid():
            current_license = DriverLicense.objects.filter(
                user_id=user_id).first()
            if current_license:
                data_by_form = form.cleaned_data
                for field, value in data_by_form.items():
                    if value and field != 'categories':
                        setattr(current_license, field, value)
                categories = data_by_form['categories']
                if categories:
                    current_license.categories.set(categories)
            else:
                license = form.save(commit=False)
                license.user_id = user_id
                license.save()
                form.save_m2m()
            messages.success(request,
                             "Данные о водительском удостоверении успешно изменены")
            logger.info(f"Сохранение данных о ВУ пользователя {user_id}")
            return redirect('show_driver_categories', user_id=user_id)
        logger.debug(f"Ошибка сохранения данных о ВУ пользователя {user_id}")
        messages.error(request, "Проверьте соответствие дат")
    else:
        form = DriverLicenseForm()
    context = {'form': form,
               'title': 'Изменение данных о водительском удостоверении',
               'view': 'change_driver_license',
               'user': get_user_by_id(user_id),
               'user_id': user_id,
               'menu': menu}
    return render(request, 'doc_app/change_driver_license.html', context=context)