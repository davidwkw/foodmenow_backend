from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, validate_password
from enum import Enum
import jwt
import datetime
from food_me_now_backend.settings import SECRET_KEY
from django.http import JsonResponse

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

    @classmethod
    def set_password(cls, password):

        # if not validate_password(password, user=None, password_validators=MinimumLengthValidator):

        password_hash = make_password(password)

        return password_hash

    def check_password(self, password):

        return check_password(password, self.password_hash)

    @classmethod
    def encode_auth_token(cls, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }

            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            print(e)
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 0
        except jwt.InvalidTokenError:
            return 0


class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    distance = models.IntegerField(blank=True, default=10)
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
