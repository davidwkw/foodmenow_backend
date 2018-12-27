import requests
import json
import re
from django.http import JsonResponse, HttpResponse
from foodmenow.models import User, Preference
from food_me_now_backend.settings import YELP_SECRET_KEY
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED
)


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

@csrf_exempt
def create_user(request):

    if request.method == 'POST':

        post_data = request.POST

        new_user = User(email=post_data.get('email', ''),
                        password_hash=User.set_password(
                        post_data.get('password', '')),
                        username=post_data.get('username', ''))

        try:
            new_user.save()

            auth_token = new_user.encode_auth_token(new_user.id)

            responseObject = {
                'status': HTTP_200_OK,
                'message': 'User successfully created.',
                'token': auth_token.decode()
            }
        except Exception as e:
            responseObject = {
                'error': e
            }

        return JsonResponse(responseObject)

    else:

        responseObject = {
            'status': HTTP_405_METHOD_NOT_ALLOWED,
            'message': 'Only GET requests are allowed'
        }

        return JsonResponse(responseObject)


@csrf_exempt
def login_user(request):

    if request.method == 'POST':

        post_data = request.POST

        user = User.objects.get(email=post_data['email'])

        if user and user.check_password(post_data['password']):

            auth_token = user.encode_auth_token(user.id)

            responseObject = {
                'status': HTTP_200_OK,
                'message': 'User successfully created.',
                'token': auth_token.decode()
            }

            return JsonResponse(responseObject)

        else:

            responseObject = {
                'status': HTTP_400_BAD_REQUEST,
                'message': 'User email or password does not exist.',
            }

            return JsonResponse(responseObject)

    else:

        responseObject = {
            'status': HTTP_405_METHOD_NOT_ALLOWED,
            'message': 'Only POST requests are allowed'
        }

        return JsonResponse(responseObject)


def update_preferences(request):

    if request.META['HTTP_AUTHORIZATION']:

        auth_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]

        user_id = User.decode_auth_token(auth_token)

        user = User.objects.get(id=user_id)

        if request.method == 'POST':

            post_data = request.POST

            user_preference = user.Preference(distance=post_data.get('distance', ''),
                                              price_min=post_data.get(
                'price_min', ''),
                price_max=post_data.get(
                'price_max', ''),
                rating_min=post_data.get(
                'rating_min', ''),
                rating_max=post_data.get(
                'rating_max', ''),
                food_genre=post_data.get('food_genre', ''))

            user_preference.save()

            responseObject = {
                'status': HTTP_200_OK,
                'message': 'User preference successfully created.',
            }

            return JsonResponse(responseObject)

        elif request.method == 'PUT':

            post_data = request.PUT

        else:

            responseObject = {
                'status': HTTP_405_METHOD_NOT_ALLOWED,
                'message': 'Only POST requests are allowed'
            }

            return JsonResponse(responseObject)

    else:

        responseObject = {
            'status': HTTP_401_UNAUTHORIZED,
            'message': 'Only POST requests are allowed'
        }

        return JsonResponse(responseObject)
