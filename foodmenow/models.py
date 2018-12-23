from django.db import models
from django.contrib.postgres.fields import ArrayField
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
    private = models.BooleanField(default=False)

    def __str__(self):
        return f'User {self.id}'

    class Meta:
        verbose_name_plural = 'Users'

class Preferences(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    distance = models.IntegerField(blank=True, default=5)
    price_min = models.CharField(max_length=5, blank=True)
    price_max = models.CharField(max_length=5, blank=True)
    rating_min = models.CharField(max_length=5, blank=True)
    rating_max = models.CharField(max_length=5, blank=True)
    food_genre = ArrayField(models.CharField(max_length=256, blank=True))
    
    def __str__(self):
        return 'Preference'

    class Meta:
        verbose_name_plural = 'Preference'