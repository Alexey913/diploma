from django import forms
from django.forms import ValidationError

from .models import Phone, Email, Contact

from datetime import date


class PhoneForm(forms.ModelForm):

    class Meta:
        model = Phone

        fields = ['phone']

        widgets = {'phone': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Номер телефона'})}


class EmailForm(forms.ModelForm):

    class Meta:
        model = Email

        fields = ['email']

        widgets = {'email': forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'})}


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        if not data['surname'] and not data['name']:
            raise ValidationError("Необходимо указать имя или фамилию")
        if data['birthday'] and data['birthday'] > date.today():
            raise ValidationError('Дата рождения не должна быть позже сегодняшней')

    class Meta:
        model = Contact

        fields = ['surname', 'name', 'patronymic',
                  'organization', 'birthday', 'place_residense']

        widgets = {'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
                   'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
                   'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
                   'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Организация'}),
                   'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                   'place_residense': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес'}), }

class SearchContactForm(forms.Form):

    contact = forms.CharField(max_length=50, min_length=2,
                                error_messages={'required': 'Заполните поле поиска'},
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control', 'placeholder': 'Контакт'}))