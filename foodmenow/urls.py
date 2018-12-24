from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'.{0,3}(latitude=(?P<latitude>-?\d+\.\d+)).{0,3}(longitude=(?P<longitude>-?\d+\.\d+))(.{0,3}radius=(?P<radius>\d+))?(.{0,3}price=(?P<price>\d))?(.{0,3}categories=(?P<categories>(\w+,?)+))?/$', views.restaurant_search),
    path('<id>/reviews/', views.restaurant_details),
    path('<id>/', views.restaurant_reviews),
    # path('create/', views.create_user),
    # path('login/', views.login_user)
]

# (r'(latitude=(?P<latitude>\d+))\s*(logitude=(?P<longitude>\d+))\s*((radius=(?P<radius>\d+)?))
# re_path(r'(latitude=(?P<latitude>\d+))\s*(logitude=(?P<longitude>\d+))\s*((radius=(?P<radius>\d+)?))', views.restaurant_search)
# path('latitude=<latitude>&logitude=<longitude>&radius=<radius>/', views.restaurant_search)
# re_path(r'(?P<latitude>-?\d+\.\d+).{1,3}(?P<longitude>-?\d+\.\d+)(.{1,3}(?P<radius>\d+))?/$', views.restaurant_search)
# re_path(r'(?P<latitude>-?\d+\.\d+)&(?P<longitude>-?\d+\.\d+)(&(?P<radius>\d+))?/$', views.restaurant_search)
