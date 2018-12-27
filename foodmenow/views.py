import requests
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from foodmenow.models import User, Preference
from food_me_now_backend.settings import YELP_SECRET_KEY
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.views import APIView


# from django.contrib.auth import login, logout
# Create your views here.

# APIs
def restaurant_search(request):

    payload = {'latitude': request.GET.get('latitude', ''),
               'longitude': request.GET.get('longitude', ''),
               'radius': request.GET.get('radius', ''),
               'price': request.GET.get('price', ''),
               'categories': request.GET.get('categories', ''),
               'term': 'restaurants',
               }

    r = requests.get('https://api.yelp.com/v3/businesses/search',
                     params=payload, headers={'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)


def restaurant_reviews(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)


def restaurant_details(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}/reviews', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)

# User related


def create_user(request):

    if request.method == 'GET':

        post_data = request.GET

        new_user = User(email=post_data.get('email', ''),
                        password_hash=User.set_password(
            post_data.get('password', '')),
            username=post_data.get('username', ''))

        new_user.save()

        auth_token = new_user.encode_auth_token(new_user.id)

        import pdb
        pdb.set_trace()

        responseObject = {
            'status': HTTP_200_OK,
            'message': 'User successfully created.',
            'token': auth_token
        }

        return JsonResponse(responseObject)


def login_user(request):

    if request.method == 'POST':

        post_data = request.data

        user = User.objects.get(email=post_data.get('email'))

        if user is None:

            return HttpResponse('User does not exist')

        elif user and user.check_password(post_data.get('password')):

            return JsonResponse({'status': 'Success'},
                                status=HTTP_200_OK)


def update_preferences(request):

    if request.method == 'POST':

        post_data = request.POST

        preference = Preference(distance=post_data.get('distance', ''),
                                price_min=post_data.get('price_min', ''),
                                price_max=post_data.get('price_max', ''),
                                rating_min=post_data.get('rating_min', ''),
                                rating_max=post_data.get('rating_max', ''),
                                food_genre=post_data.get('food_genre', ''))

        preference.save()

        responseObject = {
            'status': HTTP_200_OK,
            'message': 'Preference successfully created.',
        }

        return JsonResponse(responseObject)

    elif request.method == 'PUT':

        post_data = request.PUT

    else:

        return HttpResponse('Wrong request method')
