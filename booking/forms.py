"""
Django forms module
"""
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Creation form for CustomUser model
    """
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    """
    Edit form for CustomUser model
    """
    class Meta:
        model = CustomUser
        fields = ('email',)
