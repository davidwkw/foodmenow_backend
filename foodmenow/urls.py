from django.urls import re_path, path
from . import views

urlpatterns = [
    path('search/', views.restaurant_search),
    path('<id>/reviews/', views.restaurant_details),
    path('<id>/', views.restaurant_reviews),
    # re_path(r'search.{0,3}(latitude=(?P<latitude>-?\d+\.\d+)).{0,3}(longitude=(?P<longitude>-?\d+\.\d+))(.{0,3}radius=(?P<radius>\d+))?(.{0,3}price=(?P<price>\d))?(.{0,3}categories=(?P<categories>(\w+,?)+))?/?', views.restaurant_search),
    # path('create/', views.create_user),
    # path('login/', views.login_user)
]
