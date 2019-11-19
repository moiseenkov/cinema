import django_filters
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
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
        'showings': reverse('showing-list', request=request, format=format_),
        'tickets': reverse('ticket-list', request=request, format=format_),
        # 'pay/<int:pk>': reverse('pay', request=request, format=format_),
    })


class FilterByUserMixin:
    """
    Filters queryset by pk. Admin gets queryset with no filtering. Attribute 'user_field' must be specified
    """
    def get_queryset(self):
        user = self.request.user
        filtering = {self.user_field: user.pk}
        queryset = self.queryset if user.is_staff else self.queryset.filter(**filtering)
        return queryset.all()


class PermissionSelectorMixin:
    def get_permissions(self):
        try:
            # return permission_classes depending on `request.method`
            return [permission() for permission in self.permission_classes_by_method[self.request.method]]
        except KeyError:
            # method is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


class ProtectedErrorOnDeleteMixin:
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as ex:
            return Response(data=str(ex), status=status.HTTP_423_LOCKED)


class CustomListByUser(FilterByUserMixin, ListCreateAPIView):
    """
    Returns list of available users and allows to create new user
    """
    permission_classes = [IsAuthenticated]
    queryset = models.CustomUser.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['email', 'is_staff', 'is_active']
    user_field = 'pk'

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return serializers.CustomUserAdminSerializer
        else:
            return serializers.CustomUserSerializer


class CustomUserDetail(FilterByUserMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns user's information and allows to update and delete it
    """
    permission_classes = [IsAuthenticated]
    queryset = models.CustomUser.objects.all()
    user_field = ['pk']

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


class HallsDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin, RetrieveUpdateDestroyAPIView):
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


class MoviesDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin, RetrieveUpdateDestroyAPIView):
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


class ShowingsListView(PermissionSelectorMixin, ListCreateAPIView):
    """
    Returns list of showings and allows admin to create new showing
    """
    serializer_class = serializers.ShowingSerializer
    permission_classes = [AllowAny]
    queryset = models.Showing.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['hall', 'movie', 'date_time', 'price']

    permission_classes_by_method = {
        'POST': (IsAdminUser, ),
    }


class ShowingsDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns detailed information about showing. Admins allowed to create, update and delete it
    """
    serializer_class = serializers.ShowingSerializer
    permission_classes = [AllowAny]
    queryset = models.Showing.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser, ),
        'PATCH': (IsAdminUser, ),
        'DELETE': (IsAdminUser, ),
    }


class TicketsListView(FilterByUserMixin, ListCreateAPIView):
    """
    Returns list of showings and allows admin to create new showing
    """
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'showing', 'date_time', 'row_number', 'seat_number', 'paid']
    user_field = 'user'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            if self.request.user and self.request.user.is_staff:
                return serializers.TicketCreateAdminSerializer
            else:
                return serializers.TicketCreateSerializer
        else:
            return serializers.TicketSerializer


class TicketsDetail(FilterByUserMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns detailed information about tickets. Authenticated users allowed to create, update and delete their tickets.
    Admin allowed to create, update and delete any ticket
    """
    serializer_class = serializers.TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    user_field = 'user'


class PayForTicket(FilterByUserMixin, UpdateAPIView):
    """
    Performs payment for a booked ticket
    """
    serializer_class = serializers.PaymentSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    user_field = 'user'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'paid': True
        }
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
