import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from booking.models import CustomUser, Hall, Movie, Showing, Ticket
from cinema.settings import CINEMA_EARLIEST_TIME, CINEMA_LATEST_TIME, CINEMA_CLEANING_PERIOD_MINUTES, \
    CINEMA_COMMERCIAL_PERIOD_MINUTES


class CustomUserPasswordHashMixin:
    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
            validated_data['password'] = instance.password
        return super().update(instance, validated_data)


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

    def validate(self, attrs):
        date_time = attrs.get('date_time', None)
        errors = dict()

        if date_time is None and any([not self.partial, self.instance is None]):
            errors.setdefault('date_time', []).append('This field is required')
        elif date_time is None:
            return super(ShowingSerializer, self).validate(attrs=attrs)
        else:
            time_min = datetime.datetime.strptime(CINEMA_EARLIEST_TIME, '%H:%M').time()
            time_max = datetime.datetime.strptime(CINEMA_LATEST_TIME, '%H:%M').time()
            if not time_min <= date_time.time() <= time_max:
                errors.setdefault('date_time', []).append(f"Time value should be in interval "
                                                          f"[{time_min.isoformat()}, {time_max.isoformat()}]")
            latest_showing = Showing.objects.filter(hall=attrs.get('hall', None),
                                                    date_time__lte=date_time).order_by('-date_time').first()
            if latest_showing and latest_showing != self.instance:
                service_time = datetime.timedelta(minutes=CINEMA_CLEANING_PERIOD_MINUTES) + \
                               datetime.timedelta(minutes=CINEMA_COMMERCIAL_PERIOD_MINUTES)
                duration = latest_showing.movie.duration
                start_time = latest_showing.date_time + datetime.timedelta(minutes=duration) + service_time
                if start_time > date_time:
                    errors.setdefault('date_time', []).append(f'Hall is busy by showing {latest_showing} and '
                                                              f'it will be free at {start_time.isoformat()}')
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TicketBaseSerializer(ModelSerializer):
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

    def get_paid(self, obj=None):
        return bool(obj.receipt)


class TicketSerializer(TicketBaseSerializer):
    class Meta:
        model = TicketBaseSerializer.Meta.model
        fields = TicketBaseSerializer.Meta.fields
        read_only_fields = fields


class TicketCreateSerializer(TicketBaseSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date_time = serializers.HiddenField(default=serializers.CreateOnlyDefault(datetime.datetime.now()))

    class Meta:
        model = TicketBaseSerializer.Meta.model


class TicketCreateAdminSerializer(TicketBaseSerializer):
    date_time = serializers.HiddenField(default=serializers.CreateOnlyDefault(datetime.datetime.now()))

    class Meta:
        model = TicketBaseSerializer.Meta.model
