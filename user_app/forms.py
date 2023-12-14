from datetime import date
import re
from django import forms
from django.forms import ValidationError
from django.core.validators import RegexValidator

from string import ascii_lowercase as low_alpha
from string import ascii_uppercase as up_alpha

from .models import Data

phone_valid = RegexValidator(r'^[+]?[0-9]+$', 'Введите корректное значение номера телефона в формате 8ХХХХХХХХХХ или +7ХХХХХХХХХХ')


def check_phone_email(input_data: str) -> bool:
    if input_data.isdigit():
        return False
    parts_of_email = input_data.split('.')
    print(parts_of_email)
    if len(parts_of_email) == 2 and '@' in parts_of_email[0] and not parts_of_email[0].endswith('@') and parts_of_email[1]:
        return False
    return True


class UserFormAuth(forms.Form):
    phone_email = forms.CharField(max_length=50, min_length=6, label='Телефон / E-mail',
                                  error_messages={'required': 'Обязательно введите телефон или e-mail'},
                                  widget=forms.TextInput(attrs={
                                      'class': 'form-control', 'placeholder': 'Телефон или e-mail'}))

    password = forms.CharField(max_length=50, min_length=6, label='Пароль',
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control', 'placeholder': 'Пароль'}))

    def clean_phone_email(self):
        phone_email: str = self.cleaned_data['phone_email']
        if check_phone_email(phone_email):
            raise forms.ValidationError(
                'Введите корректный номер телефона или адрес электронной почты')
        return phone_email

    def clean_password(self):
        password: str = self.cleaned_data['password']
        if not any(map(str.isdigit, password)) or\
           not any(map(lambda x: x in low_alpha, password)) or\
           not any(map(lambda x: x in up_alpha, password)):
            raise forms.ValidationError(
                'Пароль должен содержать цифры, а также заглавные и строчные латинские буквы')
        return password


class UserFormReg(UserFormAuth):

    confirm_password = forms.CharField(max_length=50, min_length=6, label='Подтверждение пароля',
                                       error_messages={
                                           'required': 'Пароли должны совпадать'},
                                       widget=forms.PasswordInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}))

    def clean_confirm_password(self):
        if 'password' in self.cleaned_data:
            password: str = self.cleaned_data['password']
            confirm_password: str = self.cleaned_data['confirm_password']
            if password != confirm_password:
                raise forms.ValidationError('Пароли должны совпадать')
            return confirm_password

class ChangeDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].empty_label = "Не указан"

    email = forms.EmailField(required=False, label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}))
    phone = forms.CharField(max_length=20, required=False, label='Телефон', validators=[phone_valid], widget=forms.TextInput(attrs={'class':'form-control' , 'placeholder': 'Телефон', 'title':'Введите корректный номер'}))

    class Meta:
        model = Data
        fields = ['surname', 'name', 'patronymic', 'gender',
                  'birthday', 'birth_place', 'place_residense',
                  'phone', 'email']

        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес рождения'}),
            'place_residense': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес местожительства'}),
        }

    def clean_name(self):
        super().clean()
        name = self.cleaned_data['name']
        if name and re.search(r'[^а-яА-Яa-zA-Z]', name):
                raise ValidationError('Введите корректное имя')    
        return name
    
    def clean_surname(self):
        super().clean()
        surname = self.cleaned_data['surname']
        if surname and re.search(r'[^а-яА-Яa-zA-Z]', surname):
            raise ValidationError('Введите корректную фамилию')    
        return surname
    
    def clean_patronymic(self):
        super().clean()
        patronymic = self.cleaned_data['patronymic']
        if patronymic and re.search(r'[^а-яА-Яa-zA-Z]', patronymic):
            raise ValidationError('Введите корректное отчество')    
        return patronymic
    
    def clean_birthday(self):
        super().clean()
        birthday = self.cleaned_data['birthday']
        if birthday and birthday > date.today():
            raise ValidationError('Дата рождения не должна быть позже сегодняшней')   
        return birthday
    