from django.db import models
from enum import Enum

# Create your models here.

class FOOD_GENRE_CHOICES(Enum):
    MY = "Malaysian"
    CN = "Chinese"
    IN = "Indian"

class Users(models.Model):
    username = models.CharField(max_length=256)
    password_hash = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    profile_picture = models.CharField(max_length=256, blank=True )
    private = models.BooleanField(blank=True)

    def __str__(self):
        return f'User {self.id}'

    class Meta:
        verbose_name_plural = 'Users'

class Preferences(models.Model):

    user_id = models.ForeignKey(Users, models.SET_NULL, null=True)
    distance = models.IntegerField(blank=True)
    price_min = models.IntegerField(blank=True)
    price_max = models.IntegerField(blank=True)
    review_min = models.CharField(max_length=4, blank=True)
    review_max = models.CharField(max_length=4, blank=True) 
    food_genre = models.CharField(max_length=256, blank=True, choices=[(genre, genre.value) for genre in FOOD_GENRE_CHOICES])

    def __str__(self):
        return 'Preference'

    class Meta:
        verbose_name_plural = 'Preference'