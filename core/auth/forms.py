from django import forms
from django.contrib.auth.forms import UserCreationForm

from api.models import Profile


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = Profile
        fields = ('username', 'name', 'email', 'password1', 'password2')