import django_filters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from booking.models import CustomUser
from booking.serializers import CustomUserSerializer, CustomUserAdminSerializer


@api_view(['GET'])
def api_root(request, format_=None):
    """
    Represents API Root page
    """
    return Response({
        'users': reverse('user-list', request=request, format=format_),
        'token': reverse('token', request=request, format=format_),
        'token/refresh': reverse('token-refresh', request=request, format=format_),
    })


class UsersFilterMixin:
    """
    Custom GenericAPIView
    """
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset if user.is_staff else self.queryset.filter(pk=user.pk)
        return queryset.all()


class CustomUsersList(UsersFilterMixin, ListCreateAPIView):
    """
    Returns list of available users and allows to create new user
    """
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['email', 'is_staff', 'is_active']

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return CustomUserAdminSerializer
        else:
            return CustomUserSerializer


class CustomUserDetail(UsersFilterMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns user's information and allows to update and delete it
    """
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return CustomUserAdminSerializer
        else:
            return CustomUserSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
