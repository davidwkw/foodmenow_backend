from django.urls import re_path, path
from . import views

urlpatterns = [
    path('businesses/search/', views.restaurant_search),
    path('businesses/<id>/reviews/', views.restaurant_reviews),
    path('businesses/<id>/', views.restaurant_details),
    path('user/create/', views.create_user),
    path('user/login/', views.login_user),
    path('user/update/preferences/', views.update_preferences),
    path('user/preferences/', views.user_preferences),
    path('uber/request/', views.uber_request)
]

# re_path(r'search.{0,3}(latitude=(?P<latitude>-?\d+\.\d+)).{0,3}(longitude=(?P<longitude>-?\d+\.\d+))(.{0,3}radius=(?P<radius>\d+))?(.{0,3}price=(?P<price>\d))?(.{0,3}categories=(?P<categories>(\w+,?)+))?/?', views.restaurant_search),
