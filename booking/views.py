import django_filters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from booking import serializers
from booking import models


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
        'movies': reverse('movie-list', request=request, format=format_),
    })


class UsersFilterMixin:
    """
    Custom GenericAPIView
    """
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset if user.is_staff else self.queryset.filter(pk=user.pk)
        return queryset.all()


class PermissionSelectorMixin:
    def get_permissions(self):
        try:
            # return permission_classes depending on `request.method`
            return [permission() for permission in self.permission_classes_by_method[self.request.method]]
        except KeyError:
            # method is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


class CustomUsersList(UsersFilterMixin, ListCreateAPIView):
    """
    Returns list of available users and allows to create new user
    """
    permission_classes = [IsAuthenticated]
    queryset = models.CustomUser.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['email', 'is_staff', 'is_active']

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return serializers.CustomUserAdminSerializer
        else:
            return serializers.CustomUserSerializer


class CustomUserDetail(UsersFilterMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns user's information and allows to update and delete it
    """
    permission_classes = [IsAuthenticated]
    queryset = models.CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return serializers.CustomUserAdminSerializer
        else:
            return serializers.CustomUserSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HallsList(PermissionSelectorMixin, ListCreateAPIView):
    """
    Returns list of cinema halls and allows admin to create new hall
    """
    serializer_class = serializers.HallSerializer
    permission_classes = [AllowAny]
    queryset = models.Hall.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', ]

    permission_classes_by_method = {
        'POST': (IsAdminUser, ),
    }


class HallsDetail(PermissionSelectorMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns detailed information about cinema hall. Admins allowed to create, update and delete it
    """
    serializer_class = serializers.HallSerializer
    permission_classes = [AllowAny]
    queryset = models.Hall.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser, ),
        'PATCH': (IsAdminUser,),
        'DELETE': (IsAdminUser,),
    }


class MoviesListView(PermissionSelectorMixin, ListCreateAPIView):
    """
    Returns list of movies and allows admin to create movie
    """
    serializer_class = serializers.MovieSerializer
    permission_classes = [AllowAny]
    queryset = models.Movie.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', 'duration', 'premiere_year']

    permission_classes_by_method = {
        'POST': (IsAdminUser,),
    }


class MoviesDetail(PermissionSelectorMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns detailed information about cinema hall. Admins allowed to create, update and delete it
    """
    serializer_class = serializers.MovieSerializer
    permission_classes = [AllowAny]
    queryset = models.Movie.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser, ),
        'PATCH': (IsAdminUser,),
        'DELETE': (IsAdminUser,),
    }
