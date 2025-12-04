from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя."""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля пользователя."""

    password = None

    class Meta:
        model = User
        fields = ("email", "avatar", "phone", "country")
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+7 (999) 123-45-67"}),
            "country": forms.TextInput(attrs={"placeholder": "Россия"}),
        }
