from rest_framework.serializers import ModelSerializer

from booking.models import CustomUser


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
