from django.urls import path
from . import views

urlpatterns = [
    path('', views.bussiness_search)
]