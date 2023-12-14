from django import forms
from django.forms import ValidationError

from .models import Property, Transport, Realty

from datetime import date


class PropertyForm(forms.ModelForm):

    def clean_date_registration(self):
        date_registration = self.cleaned_data['date_registration']
        if date_registration > date.today():
            raise ValidationError('Дата не должна быть позже сегодняшней')
        return date_registration

    class Meta:
        model = Property

        fields = ['date_registration', 'description']
        
        widgets = {
            'date_registration': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={
                'class':'form-control', 'placeholder': 'Описание'}),
                }

class TransportForm(PropertyForm):

    def clean_year_release(self):
        year_release = self.cleaned_data['year_release']
        if year_release and len(str(year_release)) != 4 or year_release > date.today().year:
            raise ValidationError('Введите корректное значение года')
        return year_release
    
    
    class Meta(PropertyForm.Meta):
        model = Transport

        fields = ['type_property', 'brand', 'model', 'year_release',
                  'power_engine', 'weigth', 'carrying'] + PropertyForm.Meta.fields

        widget_list = {
            'brand': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Марка'}),
            'model': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Модель'}),
            'year_rlease': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Год выпуска'}),
            'power_engine': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Мощность двигателя'}),
            'weigth': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Масса'}),    
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Регистрационный номер'}),
            'carrying': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Грузоподъемность'}),
                }
        
        widgets = PropertyForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v


class RealtyForm(PropertyForm):


    def clean_cadastral_number(self):
        cadastral_number = self.cleaned_data['cadastral_number']
        try:
            int(cadastral_number.replace(':', ''))
        except:
            raise ValidationError('Кадастровый номер должен содеражть только цифры и ":"')
        if not ':' in cadastral_number:
            raise ValidationError('Введите корректный кадастровый номер')
        return cadastral_number
    

    class Meta(PropertyForm.Meta):
        
        model = Realty

        fields = ['type_property', 'cadastral_number', 'cadastral_cost',
                  'adress', 'area'] + PropertyForm.Meta.fields

        widget_list = {
            'cadastral_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Кадастровый номер'}),
            'cadastral_cost': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Кадастровая стоимость'}),
            'adress': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Адрес объекта'}),
            'area': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Площадь объекта'}),
                }
        
        widgets = PropertyForm.Meta.widgets
        for k, v in widget_list.items():
            widgets[k] = v