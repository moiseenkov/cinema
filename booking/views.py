from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from booking.models import CustomUser
from booking.serializers import CustomUserSerializer


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
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class CustomUserDetail(UsersFilterMixin, RetrieveUpdateDestroyAPIView):
    """
    Returns user's information and allows to update and delete it
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
