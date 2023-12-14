from django import forms
from django.forms import ValidationError

from .models import Diploma

from datetime import date


class DiplomaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].empty_label = "Выберите тип документа"
    
    def clean_year_of_start_edu(self):
        year_of_start_edu = self.cleaned_data['year_of_start_edu']
        if year_of_start_edu and (len(str(
            year_of_start_edu)) != 4 or year_of_start_edu > date.today().year):
            raise ValidationError('Введите корректное значение года')
        return year_of_start_edu
    
    def clean_year_of_finish_edu(self):
        year_of_start_edu = self.cleaned_data['year_of_start_edu']
        year_of_finish_edu = self.cleaned_data['year_of_finish_edu']
        if year_of_finish_edu and (len(str(
            year_of_finish_edu)) != 4 or year_of_finish_edu > date.today().year):
            raise ValidationError('Введите корректное значение года')
        if year_of_start_edu and year_of_finish_edu and year_of_finish_edu < year_of_start_edu: 
            raise ValidationError('Год окончания не может быть меньше года начала')
        return year_of_start_edu

    def clean_date_registration(self):
        date_registration = self.cleaned_data['date_registration']
        if date_registration and date_registration > date.today():
            raise ValidationError('Дата не должна быть позже сегодняшней')
        return date_registration

    class Meta:
        model = Diploma

        fields = ['name', 'series', 'number', 'date_registration',
                  'registration_number', 'name_institution',
                  'year_of_start_edu', 'year_of_finish_edu',
                  'spiciality', 'spicialization', 'description']
        
        widgets = {
            'series': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Серия'}),
            'number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Номер'}),
            'date_registration': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Регистрационный номер'}),
            'name_institution': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Учебное заведение'}),
            'year_of_start_edu': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Начало обучения'}),
            'year_of_finish_edu': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Окончание обучения'}),
            'spiciality': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Специальность'}),
            'spicialization': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Специализация'}),
            'description': forms.Textarea(attrs={
                'class':'form-control',
                'placeholder': 'Дополнительные сведения'}),
                }