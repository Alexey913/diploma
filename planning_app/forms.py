from django import forms

from django.forms import ValidationError

from .models import Remind

class RemindForm(forms.ModelForm):

    class Meta:
        model = Remind

        fields = ['title', 'date', 'time', 'all_day', 'repeat', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Описание события'}),
        }

class SearchRemindTitleForm(forms.Form):

    title = forms.CharField(max_length=50, min_length=2,
                                error_messages={'required': 'Заполните поле поиска'},
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control', 'placeholder': 'Заголовок'}))


class SearchRemindDateForm(forms.Form):

    start_date = forms.DateField(error_messages={'required': 'Заполните поле поиска'},
                                widget=forms.DateInput(
                                    attrs={'class': 'form-control', 'type': 'date'}))
    end_date = forms.DateField(error_messages={'required': 'Заполните поле поиска'},
                                widget=forms.DateInput(
                                    attrs={'class': 'form-control', 'type': 'date'}))
    
    # def clean_end_date(self):
    #     end_date = self.cleaned_data['end_date']
    #     start_date = self.cleaned_data['start_date']
    #     if start_date < end_date:
    #         raise ValidationError('Введите корректные даты')   
    #     return end_date
    
