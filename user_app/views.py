import hashlib
import os

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages

import logging

from .forms import ChangeDataForm, UserFormReg, UserFormAuth

from .models import User, Data

from abstract_app.views import menu, check_authorization, get_data_with_verbose_name, redirect_with_error


logger = logging.getLogger(__name__)


def pass_to_hash(password: str) -> (str, str):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 1_000_000)
    return key, salt


def fill_email(input_data: str) -> str:
    if '@' in input_data:
        return input_data
    return None


def fill_phone(input_data: str) -> str:
    if input_data.isdigit():
        return input_data
    return None


def get_user(phone_email: str) -> User:
    email = fill_email(phone_email)
    phone = fill_phone(phone_email)
    if email:
        return User.objects.filter(email=email).first()
    elif phone:
        return User.objects.filter(phone=phone).first()


def check_user_pass(phone_email: str, password: str) -> bool:
    extention_user = get_user(phone_email)
    if extention_user:
        user_salt = extention_user.salt
        user_password = hashlib.pbkdf2_hmac('sha256',
                                            password.encode('utf-8'),
                                            user_salt,
                                            1_000_000)
        if user_password == extention_user.hash_password:
            return True
    return False


def create_data(user: User):
    data = Data.objects.create(user=user)
    data.save()


def enter_office(request: HttpResponse, phone_email: str, password: str) -> HttpResponse:
    user_id = get_user(phone_email).pk
    request.session['pk'] = user_id
    logger.info(f'Вход в систему пользователя {user_id}')
    return redirect(show_data, user_id=user_id)



def main(request):
    user_id = request.session['pk'] if 'pk' in request.session else None
    if user_id:
        return redirect(show_data, user_id=user_id)
    return redirect_with_error(request)


def registration(request):
    if request.method == 'POST':
        form = UserFormReg(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            phone_email = data['phone_email']
            password = data['password']
            hash_password, salt = pass_to_hash(password)
            if not get_user(phone_email):
                user = User(phone=fill_phone(phone_email),
                            email=fill_email(phone_email),
                            salt=salt,
                            hash_password=hash_password)
                user.save()
                create_data(user)
                logger.info(f'Создан пользователь {user}')
                messages.success(request, "Пользователь успешно создан!")
                return enter_office(request, phone_email, password)
            else:
                logger.debug('Ошибка создания пользователя - пользователь существует')
                messages.error(request, "Пользователь с таким e-mail или телефоном уже существует!")
    else:
        form = UserFormReg()
    context = {'form': form,
               'title': 'Регистрация',
               'user_id': None,
               'menu': menu}
    return render(request, 'user_app/registration.html', context=context)



def authorization(request):
    if request.method == 'POST':
        form = UserFormAuth(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            phone_email = data['phone_email']
            password = data['password']
            if check_user_pass(phone_email, password):
                return enter_office(request, phone_email, password)
        logger.debug('Неверный логин или пароль')
        messages.error(request, "Неверный логин или пароль")
    else:
        form = UserFormAuth()
    context = {'form': form,
               'title': 'Авторизация',
               'user_id': None,
               'menu': menu}
    return render(request, 'user_app/authorization.html', context=context)


def logout(request):
    try:
        logger.info(f"Выход пользователя {request.session['pk']}")
        del request.session['pk']
    except:
        return redirect('authorization')
    return redirect('authorization')


@check_authorization
def show_data(request, user_id):
    data = Data.objects.values('surname', 'name', 'patronymic', 'birthday',
                                'birth_place', 'place_residense', 'gender').filter(user_id=user_id).first()
    object_data = get_object_or_404(Data, user_id=user_id)
    context = get_data_with_verbose_name(object_data, data)
    user = object_data.user
    if user.email: context['E-mail'] = user.email
    if user.phone: context['Телефон'] = user.phone
    context_to_template = {'context': context,
                            'title': 'Данные пользователя',
                            'user_id': user_id,
                            'menu': menu,
                            'user_name': object_data}
    return render(request, 'user_app/data.html', context=context_to_template)


@check_authorization
def change_data(request, user_id):
    if request.method == 'POST':
        form = ChangeDataForm(request.POST)
        if form.is_valid():
            current_data = Data.objects.get(user_id=user_id)
            current_user = User.objects.get(pk=user_id)
            if current_data:
                data_by_form = form.cleaned_data
                for field, value in data_by_form.items():
                    if value and field != 'phone' and field != 'email':
                        setattr(current_data, field, value)
                current_data.save()
                phone = data_by_form['phone']
                email = data_by_form['email']
                if phone:
                    if get_user(phone):
                        messages.error(request, "Номер телефона зарегистрирован другим пользователем")
                    else:
                        current_user.phone = phone
                if email:
                    if get_user(email):
                        messages.error(request, "E-mail зарегистрирован другим пользователем")
                    else:
                        current_user.email = email    
                current_user.save()
            else:
                form.save()
            logger.info(f'Успешное сохранение данных пользователя {user_id}')
            messages.success(request, "Данные успешно изменены")
            return redirect(show_data, user_id=user_id)
        messages.error(request, "Неверные данные")
        logger.warning(f'Ошибка ввода данных пользователя {user_id}')
    else:
        form = ChangeDataForm()
    context = {'form': form,
            'title': 'Изменение личных данных',
            'user_id': user_id,
            'user_name': Data.objects.get(user_id=user_id),
            'menu': menu}
    return render(request, 'user_app/change_data.html', context=context)
