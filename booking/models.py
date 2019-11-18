from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    class Meta:
        ordering = ['-id']

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()


class Hall(models.Model):
    name = models.fields.CharField(verbose_name='Hall name', max_length=32, blank=False, unique=True)
    rows_count = models.fields.IntegerField(verbose_name='Rows count', validators=[MinValueValidator(1)])
    rows_size = models.fields.IntegerField(verbose_name='Rows size (seats count)', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Cinema hall'
        verbose_name_plural = 'Cinema halls'
        ordering = ['-id']

    def __str__(self):
        return str(self.name) + ' (' + str(self.rows_count) + 'x' + str(self.rows_size) + ')'


class Movie(models.Model):
    name = models.fields.CharField(verbose_name='Title', max_length=128, blank=False)
    duration = models.fields.IntegerField(verbose_name='Duration', validators=[MinValueValidator(1)])
    premiere_year = models.IntegerField(verbose_name='Premiere Year', validators=[MinValueValidator(1896)],
                                        blank=True, null=True)

    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
        ordering = ['-id']
        unique_together = ['name', 'premiere_year']

    def __str__(self):
        return str(self.name) + (" (" + str(self.premiere_year) + ")") or ''


class Showing(models.Model):
    hall = models.ForeignKey(to=Hall, on_delete=models.PROTECT)
    movie = models.ForeignKey(to=Movie, on_delete=models.PROTECT)
    date_time = models.DateTimeField()
    price = models.DecimalField(max_digits=32, decimal_places=2, validators=[MinValueValidator(0.0)])

    class Meta:
        verbose_name = 'Showing'
        verbose_name_plural = 'Showings'
        ordering = ['-date_time']
        unique_together = ['hall', 'movie', 'date_time']

    def __str__(self):
        return str(self.movie) + ', ' + str(self.date_time) + ', ' + str(self.hall) + ', $' + str(self.price)


class Ticket(models.Model):
    showing = models.ForeignKey(to=Showing, on_delete=models.PROTECT)
    user = models.ForeignKey(to=CustomUser, on_delete=models.PROTECT)
    date_time = models.DateTimeField()
    row_number = models.IntegerField(verbose_name='Row number', validators=[MinValueValidator(1)])
    seat_number = models.IntegerField(verbose_name='Seat number in row', validators=[MinValueValidator(1)])
    paid = models.BooleanField(verbose_name='Paid', default=False)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-id']
        unique_together = ['showing', 'row_number', 'seat_number']

    def __str__(self):
        return ', '.join((str(value) for value in ['Ticket for', self.showing, 'user', self.user, self.date_time]))
