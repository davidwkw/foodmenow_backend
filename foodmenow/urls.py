from django.urls import re_path, path
from . import views

urlpatterns = [
    path('businesses/search/', views.restaurant_search),
    path('businesses/<id>/reviews/', views.restaurant_details),
    path('businesses/<id>/', views.restaurant_reviews),
    path('user/create/', views.create_user),
    path('user/login/', views.login_user),
    path('user/update/<id>/preference/', views.update_preferences)
]

# re_path(r'search.{0,3}(latitude=(?P<latitude>-?\d+\.\d+)).{0,3}(longitude=(?P<longitude>-?\d+\.\d+))(.{0,3}radius=(?P<radius>\d+))?(.{0,3}price=(?P<price>\d))?(.{0,3}categories=(?P<categories>(\w+,?)+))?/?', views.restaurant_search),
