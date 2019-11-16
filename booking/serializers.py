from rest_framework.serializers import ModelSerializer

from booking.models import CustomUser


class CustomUserCreateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', ]


class CustomUserAdminSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_staff', 'is_active', ]
