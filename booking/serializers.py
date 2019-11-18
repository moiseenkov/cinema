import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from booking.models import CustomUser, Hall, Movie, Showing
from cinema.settings import CINEMA_EARLIEST_TIME, CINEMA_LATEST_TIME


class CustomUserPasswordHashMixin:
    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(CustomUserPasswordHashMixin, ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']


class CustomUserAdminSerializer(CustomUserPasswordHashMixin, ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_staff', 'is_active', 'password']


class HallSerializer(ModelSerializer):
    seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = ['id', 'name', 'rows_count', 'rows_size', 'seats_count']

    def get_seats_count(self, obj):
        return obj.rows_count * obj.rows_size


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'name', 'duration', 'premiere_year']


class ShowingSerializer(ModelSerializer):
    class Meta:
        model = Showing
        fields = ['id', 'hall', 'movie', 'date_time', 'price']