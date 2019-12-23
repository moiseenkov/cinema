"""
Django admin settings for booking app
"""
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from booking.forms import CustomUserCreationForm, CustomUserChangeForm
from booking import models


class CustomUserAdmin(UserAdmin):
    """Admin class for CustomUser model"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = models.CustomUser
    list_display = ('id', 'email', 'is_staff', 'is_active',)
    list_filter = ('id', 'email', 'is_staff', 'is_active',)
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
    readonly_fields = ('id', )


class HallAdmin(ModelAdmin):
    """Admin class for Hall model"""
    list_display = ('id', 'name', 'rows_count', 'rows_size')
    readonly_fields = ('id', )


class MovieAdmin(ModelAdmin):
    """Admin class for Movie model"""
    list_display = ('id', 'name', 'duration', 'premiere_year')
    readonly_fields = ('id', )


class ShowingAdmin(ModelAdmin):
    """Admin class for Showing model"""
    list_display = ('id', 'hall', 'movie', 'date_time', 'price')
    readonly_fields = ('id', )


class TicketAdmin(ModelAdmin):
    """Admin class for Ticket model"""
    list_display = ('id', 'user', 'showing', 'date_time', 'row_number', 'seat_number', 'receipt')
    readonly_fields = ('id', 'user', 'date_time', 'receipt')


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.Hall, HallAdmin)
admin.site.register(models.Movie, MovieAdmin)
admin.site.register(models.Showing, ShowingAdmin)
admin.site.register(models.Ticket, TicketAdmin)
