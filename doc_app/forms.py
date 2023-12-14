from django import forms
from django.core.validators import RegexValidator
from django.forms import ValidationError

import re

from datetime import date

from .models import Spouce, Children, DriverCategoryShedule, Passport, Inn, Snils, DriverLicense, ForeignPassport, MilitaryTicket, DocTemplate

number_valid = RegexValidator(
    r'^[0-9]+$', 'Введите корректное значение номера')


class DocForm(forms.ModelForm):
    def clean_date_registration(self):
        date_registration = self.cleaned_data['date_registration']
        if date_registration > date.today():
            raise ValidationError('Дата не должна быть позже сегодняшней')
        return date_registration
    
    class Meta:
        model = DocTemplate

        fields = ['series', 'number', 'date_registration',
                  'id_inspection', 'name_inspection']

        widgets = {
            'series': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Серия'}),
            'number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Номер'}),
            'date_registration': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}),
            'id_inspection': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Код подразделения'}),
            'name_inspection': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Название подразделения'}),
        }


class PassportForm(DocForm):

    def clean_date_adress_reg(self):
        date_adress_reg = self.cleaned_data['date_adress_reg']
        if date_adress_reg and date_adress_reg > date.today():
            raise ValidationError('Дата не должна быть позже сегодняшней')
        return date_adress_reg
    
    class Meta(DocForm.Meta):
        model = Passport
        fields = DocForm.Meta.fields + \
            ['adress_registration', 'adress_reg_eq_place', 'date_adress_reg']
        widget_list = {
            'adress_registration': forms.TextInput(attrs={'class': 'form-control', 
                                                          'placeholder': 'Адрес регистрации'}),
            'adress_reg_eq_place': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_adress_reg': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        widgets = DocForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v


class InnForm(DocForm):

    class Meta(DocForm.Meta):
        model = Inn
        fields = ['inn'] + DocForm.Meta.fields
        widgets = DocForm.Meta.widgets
        widgets['inn'] = forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'ИНН',
                                                'title': 'Введите корректный ИНН'})


class SnilsForm(DocForm):

    class Meta(DocForm.Meta):
        model = Snils
        widgets = DocForm.Meta.widgets
        exclude = ['series']
        

class DriverLicenseForm(DocForm):

    class Meta(DocForm.Meta):
        model = DriverLicense
        fields = DocForm.Meta.fields + \
            ['date_end_action', 'categories', 'date_start_expirience', 'special_marks']
        widget_list = {
            'date_end_action': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'date_start_expirience': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'special_marks': forms.TextInput(attrs={'class':'form-control',
                                                   'placeholder': 'Особые отметки'}),
            'categories': forms.CheckboxSelectMultiple(),
        }
        widgets = DocForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v


class DriverCategoryEditForm(forms.ModelForm):
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(DocForm.Meta):
        model = DriverCategoryShedule
        fields = ['date_begin', 'date_end', 'note']
        widgets = {
            'date_begin': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'date_end': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'note': forms.TextInput(attrs={'class':'form-control',
                                                   'placeholder': 'Отметка о категории'}),
        }

    def clean_date_begin(self):
        super().clean()
        date_begin = self.cleaned_data['date_begin']
        if date_begin and date_begin > date.today():
            raise ValidationError('Дата не должна быть позже сегодняшней')    
        return date_begin
    
    def clean_date_end(self):
        super().clean()
        date_end = self.cleaned_data['date_end']
        date_begin = self.cleaned_data['date_begin']
        if date_begin and date_end and date_begin > date_end:
            raise ValidationError(
                'Дата окончания стажа не должна быть меньше даты начала')        
        return date_end


class DriverCategoryAddForm(DriverCategoryEditForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Не выбрана"

    class Meta(DriverCategoryEditForm.Meta):
        model = DriverCategoryShedule
        fields = ['category'] + DriverCategoryEditForm.Meta.fields
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date_begin': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'date_end': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'note': forms.TextInput(attrs={'class':'form-control',
                                                   'placeholder': 'Отметка о категории'}),
        }


class MilitaryTicketForm(DocForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Не указана"

    class Meta(DocForm.Meta):
        model = MilitaryTicket
        fields = DocForm.Meta.fields + \
            ['category', 'speciality', 'description']
        widget_list = {
            'speciality': forms.TextInput(attrs={'class':'form-control',
                                                 'placeholder': 'Военная специальность'}),
            'description': forms.Textarea(attrs={'class':'form-control',
                                                 'placeholder': 'Дополнительные сведения'}),
        }
        widgets = DocForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v

class ForeignPassportForm(DocForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(DocForm.Meta):
        model = ForeignPassport
        fields = DocForm.Meta.fields + \
            ['date_end_action', 'foreign_name', 'foreign_surname']
        widget_list = {
            'date_end_action': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'foreign_name': forms.TextInput(attrs={'class':'form-control',
                                                   'placeholder': 'Имя латиницей'}),
            'foreign_surname': forms.TextInput(attrs={'class':'form-control',
                                                     'placeholder': 'Фамилия латиницей'})
        }
        
        widgets = DocForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v

    def clean_date_end_action(self):
        super().clean()
        date_end_action = self.cleaned_data['date_end_action']
        try:
            date_registration = self.cleaned_data['date_registration']
            if date_end_action < date_registration:
                raise ValidationError(
                    'Дата окончания действия не должна быть меньше даты выдачи') 
        except:
            raise ValidationError('Проверьте дату выдачи паспорта')
        return date_end_action
            
    def clean_foreign_name(self):
        super().clean()
        foreign_name = self.cleaned_data['foreign_name']
        if re.search(r'[^a-zA-Z]', foreign_name):
            raise ValidationError('Имя должно быть написано только латиницей')    
        return foreign_name
    
    def clean_foreign_surname(self):
        super().clean()
        foreign_surname = self.cleaned_data['foreign_surname']
        if re.search(r'[^a-zA-Z]', foreign_surname):
            raise ValidationError('Фамилия должна быть написана только латиницей')    
        return foreign_surname
    

class ChildrenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].empty_label = "Не указан"

    def clean_birthday(self):
        super().clean()
        birthday = self.cleaned_data['birthday']
        if birthday and birthday > date.today():
            raise ValidationError('Дата рождения не должна быть позже сегодняшней')   
        return birthday
    
    class Meta:
        model = Children
        fields = ['surname', 'name', 'patronymic', 'birthday', 'gender']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class SpouceForm(ChildrenForm):

    def clean_date_marriage(self):
        super().clean()
        date_marriage = self.cleaned_data['date_marriage']
        birthday = self.cleaned_data['birthday']
        if date_marriage and date_marriage > date.today():
            raise ValidationError(
                'Дата регистрации брака не должна быть позже сегодняшней')
        if birthday and date_marriage and date_marriage < birthday:
            raise ValidationError(
                'Дата регистрации брака не должна быть меньше даты рождения')
        return date_marriage
    
    class Meta(Children.Meta):
        model = Spouce
        fields = ChildrenForm.Meta.fields + ['date_marriage']

        widgets = ChildrenForm.Meta.widgets
        widgets['date_marriage'] = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'})