from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, validate_password
from enum import Enum

# Create your models here.


class FOOD_GENRE_CHOICES(Enum):
    MY = "Malaysian"
    CN = "Chinese"
    IN = "Indian"


class User(models.Model):
    username = models.CharField(max_length=256)
    password_hash = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    profile_picture = models.CharField(max_length=256, blank=True)
    private = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Users'
        db_table = 'users'

    def __str__(self):
        return f'User {self.id}'

    def set_password(self, password):

        if validate_password(password, password_validators=[
                CommonPasswordValidator, MinimumLengthValidator]):

            return make_password(password)

    def check_password(self, password):

        return check_password(password, self.password_hash)


class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    distance = models.IntegerField(blank=True, default=5)
    price_min = models.CharField(max_length=5, blank=True)
    price_max = models.CharField(max_length=5, blank=True)
    rating_min = models.CharField(max_length=5, blank=True)
    rating_max = models.CharField(max_length=5, blank=True)
    food_genre = ArrayField(models.CharField(max_length=256, blank=True))

    class Meta:
        verbose_name_plural = 'Preference'
        db_table = 'preferences'

    def __str__(self):
        return 'Preference'
