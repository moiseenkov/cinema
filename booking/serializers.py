"""
Booking app serializers
"""
import datetime as dt
from collections import defaultdict

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from booking.models import CustomUser, Hall, Movie, Showing, Ticket
from cinema.settings import CINEMA_EARLIEST_TIME, \
    CINEMA_LATEST_TIME, \
    CINEMA_CLEANING_PERIOD_MINUTES, \
    CINEMA_COMMERCIAL_PERIOD_MINUTES


class CustomUserPasswordHashMixin:
    """
    User's password hash mixin. Prevents showing passwords as a plane text
    """

    @staticmethod
    def create(validated_data):
        """Creates user and hashes their password"""
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Updates hashed user's password"""
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
            validated_data['password'] = instance.password
        return super().update(instance, validated_data)


class CustomUserSerializer(CustomUserPasswordHashMixin, ModelSerializer):
    """User serializer"""

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']


class CustomUserAdminSerializer(CustomUserPasswordHashMixin, ModelSerializer):
    """Admin's user serializer"""

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_staff', 'is_active', 'password']


class HallSerializer(ModelSerializer):
    """Hall serializer"""
    seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = ['id', 'name', 'rows_count', 'rows_size', 'seats_count']

    @staticmethod
    def get_seats_count(obj):
        """Returns total seats count in current hall"""
        return obj.rows_count * obj.rows_size


class MovieSerializer(ModelSerializer):
    """Movie serializer"""

    class Meta:
        model = Movie
        fields = ['id', 'name', 'duration', 'premiere_year']


class ShowingSerializer(ModelSerializer):
    """Showing serializer"""

    class Meta:
        model = Showing
        fields = ['id', 'hall', 'movie', 'date_time', 'price']

    def validate(self, attrs):
        date_time = attrs.get('date_time', None)
        errors = defaultdict(list)

        if date_time is None and any([not self.partial, self.instance is None]):
            errors['date_time'].append('This field is required')
        elif date_time is None:
            return super(ShowingSerializer, self).validate(attrs=attrs)
        else:
            movie = attrs.get('movie', None)
            movie = movie or (self.instance.movie if self.instance else None)
            if movie and date_time.year < movie.premiere_year:
                errors['date_time'].append('Showing date cannot be before movie\'s premiere')

            time_min = dt.datetime.strptime(CINEMA_EARLIEST_TIME, '%H:%M').time()
            time_max = dt.datetime.strptime(CINEMA_LATEST_TIME, '%H:%M').time()
            if not time_min <= date_time.time() <= time_max:
                errors['date_time'].append(f"Time value should be in interval "
                                           f"[{time_min.isoformat()}, "
                                           f"{time_max.isoformat()}]")
            latest_showings = Showing.objects.filter(hall=attrs.get('hall', None),
                                                     date_time__lte=date_time)
            latest_showing = latest_showings.order_by('-date_time').first()
            if latest_showing and latest_showing != self.instance:
                service_time = dt.timedelta(minutes=CINEMA_CLEANING_PERIOD_MINUTES) + \
                               dt.timedelta(minutes=CINEMA_COMMERCIAL_PERIOD_MINUTES)
                duration = latest_showing.movie.duration
                start_time = \
                    latest_showing.date_time + \
                    dt.timedelta(minutes=duration) + \
                    service_time

                if start_time > date_time:
                    errors['date_time'].append(f'Hall is busy by showing '
                                               f'{latest_showing} and it will be '
                                               f'free at {start_time.isoformat()}')
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TicketBaseSerializer(ModelSerializer):
    """Ticket base serializer"""
    price = serializers.ReadOnlyField(source='showing.price')
    paid = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'showing',
            'row_number',
            'seat_number',
            'price',
            'user',
            'date_time',
            'paid',
            'receipt',
        ]

    @staticmethod
    def get_paid(obj=None):
        """Returns payment receipt"""
        return bool(obj.receipt)


class TicketSerializer(TicketBaseSerializer):
    """Ticket serializer"""

    class Meta:
        model = TicketBaseSerializer.Meta.model
        fields = TicketBaseSerializer.Meta.fields
        read_only_fields = fields


class TicketCreateSerializer(TicketBaseSerializer):
    """Creating ticket serializer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date_time = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(dt.datetime.now()))

    class Meta:
        model = TicketBaseSerializer.Meta.model
        fields = TicketBaseSerializer.Meta.fields


class TicketCreateAdminSerializer(TicketBaseSerializer):
    """Admin's creating ticket serializer"""
    date_time = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(dt.datetime.now()))

    class Meta:
        model = TicketBaseSerializer.Meta.model
        fields = TicketBaseSerializer.Meta.fields
