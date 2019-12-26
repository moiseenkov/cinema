"""
Booking app views module
"""
import datetime
import uuid

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
from booking.serializers import TicketSerializer
from booking.tasks import pay_ticket


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


class FilterByUserMixin:  # pylint: disable=too-few-public-methods
    """
    APIView mixin filters queryset instances by user (is_staff = False):
        instance.user.pk == request.user.pk

    By default queryset instances relate to CustomUser model via 'user' field,
    however it can be overridden in derived class by defining 'user_field' attribute containing
    field name that relate to CustomUer model.
    Note: FilterByUserMixin filters only for non admin users (is_staff = False).
    No filtering happens for admin
    """

    def get_queryset(self):
        """
        Overrides get_queryset() method: filters queryset by given 'user_field' with key = user.pk
        """
        user = self.request.user
        user_field = getattr(self, 'user_field', 'user')
        filtering = {user_field: user.pk}
        queryset = self.queryset if user.is_staff else self.queryset.filter(**filtering)
        return queryset.all()


class PermissionSelectorMixin:  # pylint: disable=too-few-public-methods
    """
    APIView mixin overrides APIView.get_permissions() by setting up permissions according to HTTP
    method mapping

    By default PermissionSelectorMixin creates instances for all classes in self.permission_classes,
    however it can use dict self.permission_classes_by_method where
    key - HTTP method [GET|POST|PUT|PATCH|DELETE],
    value - [PermissionClass, ]

    """

    def get_permissions(self):
        """
        Overrides get_permissions() method:
        sets permission classes according to HTTP method settings
        """
        mapping = getattr(self, 'permission_classes_by_method', None)
        method = self.request.method
        permission_classes = mapping[method] if mapping and method in mapping else \
            self.permission_classes
        return [permission() for permission in permission_classes]


class ProtectedErrorOnDeleteMixin:  # pylint: disable=too-few-public-methods
    """
    APIView mixin prevents deletion of locked objects

    Mixin catches ProtectedError exception and returns HTTP_423_LOCKED if the object was locked
    (has external references)
    """

    def delete(self, request, *args, **kwargs):
        """
        Overrides delete() method: catches ProtectedError exception and send HTTP 423
        """
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as ex:
            return Response(data=str(ex), status=status.HTTP_423_LOCKED)


class CustomUserList(FilterByUserMixin, ListCreateAPIView):
    """
    Represent users list

    Public url allows to create new user with email and password. **Email should be unique!**
    **Anonymous users** can view empty users list and allowed to create new user (non admin).
    **Users** can view paginated list of users containing only their our own information
    and allowed to create new user (non admin).
    **Admins** can view paginated users list containing all users and create new admin as well as
    non admin users.
    """
    permission_classes = [AllowAny]
    queryset = models.CustomUser.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['email', 'is_staff', 'is_active']
    user_field = 'pk'

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return serializers.CustomUserAdminSerializer
        return serializers.CustomUserSerializer


class CustomUserDetail(FilterByUserMixin, RetrieveUpdateDestroyAPIView):
    """
    Represents users detail information

    Allows users and admins view/edit/delete users by id. Users have access to their information
    only.
    """
    permission_classes = [IsAuthenticated]
    queryset = models.CustomUser.objects.all()
    user_field = 'pk'

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return serializers.CustomUserAdminSerializer
        return serializers.CustomUserSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete selected user

        DELETE requests deactivate users (is_active=False) instead of physical removal from
        database.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HallsList(PermissionSelectorMixin, ListCreateAPIView):
    """
    Represents cinema halls list

    Public url allows anyone to view cinema halls information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.HallSerializer
    permission_classes = [AllowAny]
    queryset = models.Hall.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', ]

    permission_classes_by_method = {
        'POST': (IsAdminUser,),
    }


class HallsDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin,
                  RetrieveUpdateDestroyAPIView):
    """
    Represents cinema hall detailed information

    Public url allows anyone to view cinema hall detailed information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.HallSerializer
    permission_classes = [AllowAny]
    queryset = models.Hall.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser,),
        'PATCH': (IsAdminUser,),
        'DELETE': (IsAdminUser,),
    }


class MoviesListView(PermissionSelectorMixin, ListCreateAPIView):
    """
    Represents movies list

    Public url allows anyone to view movies information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.MovieSerializer
    permission_classes = [AllowAny]
    queryset = models.Movie.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', 'duration', 'premiere_year']

    permission_classes_by_method = {
        'POST': (IsAdminUser,),
    }


class MoviesDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin,
                   RetrieveUpdateDestroyAPIView):
    """
    Represents movie detailed information

    Public url allows anyone to view movie detailed information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.MovieSerializer
    permission_classes = [AllowAny]
    queryset = models.Movie.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser,),
        'PATCH': (IsAdminUser,),
        'DELETE': (IsAdminUser,),
    }


class ShowingsListView(PermissionSelectorMixin, ListCreateAPIView):
    """
    Represents showings list

    Public url allows anyone to view showings information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.ShowingSerializer
    permission_classes = [AllowAny]
    queryset = models.Showing.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['hall', 'movie', 'date_time', 'price']

    permission_classes_by_method = {
        'POST': (IsAdminUser,),
    }


class ShowingsDetail(ProtectedErrorOnDeleteMixin, PermissionSelectorMixin,
                     RetrieveUpdateDestroyAPIView):
    """
    Represents showing detailed information

    Public url allows anyone to view showing detailed information. Only admins allowed to
    create/update/delete.
    """
    serializer_class = serializers.ShowingSerializer
    permission_classes = [AllowAny]
    queryset = models.Showing.objects.all()

    permission_classes_by_method = {
        'PUT': (IsAdminUser,),
        'PATCH': (IsAdminUser,),
        'DELETE': (IsAdminUser,),
    }


class TicketsListView(FilterByUserMixin, ListCreateAPIView):
    """
    Represents tickets list

    Url allows authenticated users to view list of their tickets and book new tickets.
    Admins can view all tickets.
    """
    serializer_class = serializers.TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'showing', 'date_time', 'row_number', 'seat_number']
    user_field = 'user'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.TicketCreateSerializer
        return serializers.TicketSerializer

    def create(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        data = request.data.copy()

        if not request.user.is_staff or request.user.is_staff and data.get('user', None) is None:
            data['user'] = request.user.pk

        date_time = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        date_time = date_time[:-3] + date_time[-2:]
        data['date_time'] = date_time

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TicketsDetail(FilterByUserMixin, RetrieveUpdateDestroyAPIView):
    """
    Represents ticket detailed information

    Url allows authenticated users to view selected ticket's  detailed information.
    Admins can view all tickets.
    """
    serializer_class = serializers.TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    user_field = 'user'

    def delete(self, request, *args, **kwargs):
        ticket = self.get_object()
        if ticket.receipt:
            return Response(data='Paid ticket cannot be removed', status=status.HTTP_423_LOCKED)
        return super(TicketsDetail, self).delete(request, *args, **kwargs)


class PayForTicket(FilterByUserMixin, UpdateAPIView):
    """
    Performs payment for a booked ticket
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Ticket.objects.all()
    user_field = 'user'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receipt:
            return Response(data=f'Ticket {instance.pk} is paid already',
                            status=status.HTTP_400_BAD_REQUEST)

        payment_uuid = uuid.uuid4()
        pay_ticket.delay(pk=instance.pk, payment_uuid=payment_uuid)
        data = {
            'receipt': payment_uuid
        }
        return Response(data=data, status=status.HTTP_200_OK)
