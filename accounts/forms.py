from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError

from .models import MyUser

class UserCreationForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ['email', 'username', 'first_name', 'last_name', 'profile_picture']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')  

        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  

        if commit:
            user.save()
        return user
        
class UserChangeForm(ModelForm):
    class Meta:
        model = MyUser
        fields = ['username', 'first_name', 'last_name', 'date_of_birth', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'flatpickr', 'placeholder': 'Select Date of Birth'})
        }