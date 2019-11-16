import django_filters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from booking.models import CustomUser, Hall
from booking.serializers import CustomUserSerializer, CustomUserAdminSerializer, HallSerializer


@api_view(['GET'])
def api_root(request, format_=None):
    """
    Represents API Root page
    """
    return Response({
        'users': reverse('user-list', request=request, format=format_),
        'token': reverse('token', request=request, format=format_),
        'token/refresh': reverse('token-refresh', request=request, format=format_),
        'halls': reverse('hall-list', request=request, format=format_),
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


class HallsList(ListCreateAPIView):
    """
    Returns list of cinema halls and allows admin to create new hall
    """
    serializer_class = HallSerializer
    permission_classes = [AllowAny]
    queryset = Hall.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', ]

    def post(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            return Response(data='You are not allowed to create halls', status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class HallsDetail(RetrieveUpdateDestroyAPIView):
    """
    Returns detailed information about cinema hall. Admins allowed to create, update and delete it
    """
    serializer_class = HallSerializer
    permission_classes = [AllowAny]
    queryset = Hall.objects.all()

    def update(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            return Response(data='You are not allowed to update halls', status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            return Response(data='You are not allowed to update halls', status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
