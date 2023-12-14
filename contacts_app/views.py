from itertools import chain
import logging
from typing import Callable

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages

from django.db import models

from django import forms

from django.db.models.query import QuerySet

from abstract_app.views import menu, check_authorization, get_data_with_verbose_name

from .models import Contact, Phone, Email
from .forms import ContactForm, PhoneForm, EmailForm, SearchContactForm


logger = logging.getLogger(__name__)


def abstract_list_contacts(request: HttpResponse, user_id: int,
                           contacts: QuerySet, mes: str, title: str) -> HttpResponse:
    context = {'title': 'Контакты',
               'user_id': user_id,
               'contacts': contacts,
               'mes': mes,
               'title': title,
               'menu': menu}
    return render(request, 'contacts_app/contacts.html', context=context)


@check_authorization
def get_contacts(request: HttpResponse, user_id: int) -> Callable:
    contacts = Contact.objects.filter(user_id=user_id).all()
    mes = 'Список контактов пуст'
    title = 'Список контактов'
    return abstract_list_contacts(request, user_id, contacts, mes, title)


@check_authorization
def show_contact(request: HttpResponse, user_id: int, contact_id: int) -> HttpResponse:
    object_contact = get_object_or_404(Contact, pk=contact_id)
    contact = Contact.objects.values('surname', 'name', 'patronymic',
                                     'organization', 'birthday',
                                     'place_residense').filter(
                                         pk=contact_id).first()
    output_contact = get_data_with_verbose_name(object_contact, contact)
    phones = Phone.objects.filter(contact_id=contact_id).all()
    emails = Email.objects.filter(contact_id=contact_id).all()
    context = {'title': 'Сведения о контакте',
               'user_id': user_id,
               'contact_id': contact_id,
               'contact': output_contact,
               'phones': phones,
               'emails': emails,
               'menu': menu}
    return render(request, 'contacts_app/show_contact.html', context=context)


@check_authorization
def add_contact(request: HttpResponse, user_id: int) -> HttpResponse:
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        phone_form = PhoneForm(request.POST)
        email_form = EmailForm(request.POST)
        if contact_form.is_valid() and phone_form.is_valid() and email_form.is_valid():
            contact = contact_form.save(commit=False)
            contact.user_id = user_id
            contact.save()
            if phone_form.has_changed():
                phone = phone_form.save(commit=False)
                phone.contact_id = contact.id
                phone.save()
            if email_form.has_changed():
                email = email_form.save(commit=False)
                email.contact_id = contact.id
                email.save()
            messages.success(request, "Контакт успешно создан")
            logger.info(f"Сохранение данных контакта {contact} пользователя {user_id}")
            return redirect('contacts', user_id=user_id)
        logger.debug(
            f"Ошибка сохранения данных контакта для пользователя {user_id}")
        messages.error(request, "Необходимо указать имя или фамилию")
    else:
        contact_form = ContactForm()
        phone_form = PhoneForm()
        email_form = EmailForm()
    context = {'form': contact_form,
               'phone_form': phone_form,
               'email_form': email_form,
               'title': 'Новый контакт',
               'user_id': user_id,
               'view': 'add_contact',
               'menu': menu}
    return render(request, 'contacts_app/new_contact.html', context=context)


def add_phone_or_email(request: HttpResponse, user_id: int,
                       contact_id: int, entity:models.Model,
                       form_type: forms.ModelForm, field: str, view: str,
                       mes_sucsess: str, mes_error:str) -> HttpResponse:
    if request.method == 'POST':
        form = form_type(request.POST)
        if form.is_valid() and form.has_changed():
            kwargs = {field: form.cleaned_data[field], 'contact_id': contact_id}
            if not entity.objects.filter(**kwargs).first():
                entity_instatnce = form.save(commit=False)
                entity_instatnce.contact_id = contact_id
                entity_instatnce.save()
                messages.success(request, mes_sucsess)
                logger.info(f"Сохранение данных контакта {contact_id} \
пользователя {user_id}")
                return redirect('show_contact', user_id=user_id, contact_id=contact_id)
            else:
                logger.debug(f"Ошибка сохранения данных контакта пользователя {user_id}")
                messages.error(request, mes_error)
        else:
            logger.debug(
                f"Ошибка сохранения данных контакта пользователя {user_id}")
            messages.error(request, "Необходимо ввести данные")
    else:
        form = form_type()
    context = {'form': form,
               'title': f'Контакт {contact_id}',
               'user_id': user_id,
               'contact_id': contact_id,
               'view': view,
               'menu': menu}
    return render(request, 'contacts_app/edit_contact.html', context=context)


@check_authorization
def add_phone(request: HttpResponse, user_id: int, contact_id: int) -> Callable:
    return add_phone_or_email(request, user_id, contact_id, Phone,
                       PhoneForm, 'phone', 'add_phone',
                       "Номер телефона добавлен",
                       "Телефон пользователя уже существует")
    

@check_authorization
def add_email(request: HttpResponse, user_id: int, contact_id: int) -> Callable:
    return add_phone_or_email(request, user_id, contact_id, Email,
                       EmailForm, 'email', 'add_email', "E-mail добавлен",
                       "E-mail пользователя уже существует")
    
    
@check_authorization
def change_phone_or_email(request: HttpResponse, user_id: int,
                          contact_id: int, instance_id,
                          entity: models.Model, form_type: forms.ModelForm,
                          field: str, note: str,
                          mes_sucsess: str, mes_error:str) -> HttpResponse:
    current_instance = entity.objects.filter(pk=instance_id).first()
    if request.method == 'POST':
        form = form_type(request.POST)
        if form.is_valid() and form.has_changed():
            input_instance = form.cleaned_data[field]
            kwargs = {field: input_instance, 'contact_id': contact_id}
            print(kwargs)
            if not entity.objects.filter(**kwargs).first():
                setattr(current_instance, field, input_instance)
                current_instance.save()
                messages.success(request, mes_sucsess)
                logger.info(f"Сохранение данных контакта {contact_id} \
пользователя {user_id}")
                return redirect('show_contact', user_id=user_id, contact_id=contact_id)
            else:
                logger.debug(f"Ошибка сохранения данных контакта пользователя \
{user_id} - {mes_error}")
                messages.error(request, mes_error)
        else:
            logger.debug(f"Ошибка сохранения данных контакта пользователя {user_id}")
            messages.error(request, "Необходимо ввести данные")
    else:
        form = form_type()
    context = {'form': form,
               'title': f'{note} {current_instance}',
               'user_id': user_id,
               'contact_id': contact_id,
               'change_pk': instance_id,
               'change_note': 'change_'+field,
               'note': note,
               'del_note': 'del_'+field,
               'menu': menu}
    return render(request, 'contacts_app/edit_contact_data.html', context=context)


@check_authorization
def change_email(request: HttpResponse, user_id: int,
                 contact_id: int, email_id: int) -> Callable:
    return change_phone_or_email(request, user_id, contact_id,
                                 email_id, Email, EmailForm, 'email',
                                 'E-mail', "E-mail изменен",
                                 "E-mail пользователя уже существует")


@check_authorization
def change_phone(request: HttpResponse, user_id: int,
                 contact_id: int, phone_id: int) -> Callable:
    return change_phone_or_email(request, user_id, contact_id,
                                 phone_id, Phone, PhoneForm, 'phone',
                                 'Телефон', "Номер телефона изменен",
                                 "Номер телефона пользователя уже существует")


def del_phone_or_email(request: HttpResponse,
                       user_id: int, contact_id: int,
                       instance_id: int, kind: str, entity:models.Model):
    try:
        entity.objects.filter(pk=instance_id).delete()
        logger.info(f"Удален {kind} {instance_id} контакта {contact_id} \
пользователя {user_id}")
        messages.success(request, "Данные контакта успешно удалены")
    except:
        logger.debug(f"Ошибка удаления {kind} {instance_id} контакта \
{contact_id} пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('show_contact', user_id=user_id, contact_id=contact_id)


@check_authorization
def del_email(request: HttpResponse, user_id: int,
                 contact_id: int, email_id: int) -> Callable:
    return del_phone_or_email(request, user_id, contact_id,
                              email_id, 'E-mail', Email)


@check_authorization
def del_phone(request: HttpResponse, user_id: int,
                 contact_id: int, phone_id: int) -> Callable:
    return del_phone_or_email(request, user_id, contact_id,
                              phone_id, 'Номер телефона', Phone)

@check_authorization
def change_contact(request: HttpResponse, user_id: int, contact_id: int) -> HttpResponse:
    current_contact = Contact.objects.filter(pk=contact_id).first()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data_by_form = form.cleaned_data
            for field, value in data_by_form.items():
                if value:
                    setattr(current_contact, field, value)
            current_contact.save()
            logger.info(f"Изменение данных о контакте {contact_id} \
пользователя {user_id}")
            messages.success(request, "Данные успешно изменены")
            return redirect('show_contact', user_id=user_id, contact_id=contact_id)
        logger.debug(
            f"Ошибка сохранения данных контакта {contact_id} пользователя {user_id}")
        messages.error(request, "Необходимо ввести имя или фамилию")
    else:
        form = ContactForm()
    context = {'form': form,
               'title': 'Изменение данных контакта',
               'user_id': user_id,
               'contact': current_contact,
               'contact_id': current_contact.pk,
               'change_pk': 0,
               'view': 'change_contact',
               'menu': menu}
    return render(request, 'contacts_app/edit_contact.html', context)


@check_authorization
def del_contact(request: HttpResponse, user_id: int, contact_id: int) -> HttpResponse:
    try:
        Contact.objects.filter(pk=contact_id).delete()
        logger.info(f"Удалены данные контакта {contact_id} пользователя {user_id}")
        messages.success(request, "Данные контакта успешно удалены")
    except:
        logger.debug(
            f"Ошибка удаления данных контакта {contact_id} пользователя {user_id}")
        messages.error(request, "Данных не сущствует")
    finally:
        return redirect('contacts', user_id=user_id)
    

def inject_form(request):
    return {"search_form":SearchContactForm()}

@check_authorization
def search(request, user_id):
    if request.method == 'POST':
        form = SearchContactForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            name_search = Contact.objects.filter(name__icontains=contact, user_id=user_id).all()
            suname_search = Contact.objects.filter(surname__icontains=contact, user_id=user_id).all()
            patronymic_search = Contact.objects.filter(
                patronymic__icontains=contact, user_id=user_id).all()
            organization_search = Contact.objects.filter(
                organization__icontains=contact, user_id=user_id).all()
            place_rsidense_search = Contact.objects.filter(
                place_residense__icontains=contact, user_id=user_id).all()
            contacts = list(chain(name_search, suname_search,
                                     patronymic_search, organization_search, place_rsidense_search))
            mes = 'По Вашему запросу ничего не найдено'
            title_templ = f'Найдено по запросу {contact}:'
            return abstract_list_contacts(request, user_id, contacts, mes, title_templ)
    else:
        form = SearchContactForm()
    return redirect('search', user_id=user_id)