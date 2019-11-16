from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from booking.forms import CustomUserCreationForm, CustomUserChangeForm
from booking.models import Hall, Movie
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class HallAdmin(ModelAdmin):
    list_display = ('id', 'name', 'rows_count', 'rows_size')
    readonly_fields = ('id', )


class MovieAdmin(ModelAdmin):
    list_display = ('id', 'name', 'duration', 'premiere_year')
    readonly_fields = ('id', )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hall, HallAdmin)
admin.site.register(Movie, MovieAdmin)
