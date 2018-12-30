import requests
import json
import re
from django.core import serializers
from django.http import JsonResponse, HttpResponse, QueryDict
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
# Create your views here.

# APIs


@csrf_exempt
def restaurant_search(request):

    if request.META['HTTP_AUTHORIZATION']:

        auth_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]

        user_id = User.decode_auth_token(auth_token)

        user = User.objects.get(id=user_id)

        if user:

            category_list = [", ".join(user.preference.food_genre)]

            import pdb
            pdb.set_trace()

            payload = {'latitude': request.GET.get('latitude', ''),
                       'longitude': request.GET.get('longitude', ''),
                       'radius': user.preference.distance,
                       'price': user.preference.price_max,
                       'categories': category_list,
                       'term': 'restaurants',
                       }

            r = requests.get('https://api.yelp.com/v3/businesses/search',
                             params=payload, headers={'Authorization': f'Bearer {YELP_SECRET_KEY}'})

            data = r.json()

            return JsonResponse(data)

        else:

            responseObject = {
                'status': HTTP_401_UNAUTHORIZED,
                'message': 'Invalid authorization token'
            }

            return JsonResponse(responseObject)

    else:

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


@csrf_exempt
def restaurant_reviews(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)


@csrf_exempt
def restaurant_details(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}/reviews', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)

# User related


@csrf_exempt
def create_user(request):

    if request.method == 'POST':

        post_data = json.loads(request.body.decode())

        new_user = User(email=post_data['email'],
                        password_hash=User.set_password(
                        post_data['password']),
                        username=post_data.get('username', ''))

        new_user.save()
        new_user_preference = Preference(user=new_user,
                                         distance=post_data.get(
                                             'distance', '10000'),
                                         price_min=post_data.get(
                                             'price_min', '1'),
                                         price_max=post_data.get(
                                             'price_max', '4'),
                                         rating_min=post_data.get(
                                             'rating_min', '1'),
                                         rating_max=post_data.get(
                                             'rating_max', '4'),
                                         food_genre=[post_data.get(
                                             'food_genre', '')]
                                         )

        new_user_preference.save()

        auth_token = new_user.encode_auth_token(new_user.id)

        responseObject = {
            'status': HTTP_200_OK,
            'message': 'User successfully created.',
            'token': auth_token.decode()
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

        post_data = json.loads(request.body.decode())

        user = User.objects.get(email=post_data['email'])

        if user and user.check_password(post_data['password']):

            auth_token = user.encode_auth_token(user.id)

            responseObject = {
                'status': HTTP_200_OK,
                'message': 'User successfully logged in.',
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


@csrf_exempt
def update_preferences(request):

    if request.META['HTTP_AUTHORIZATION']:

        auth_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]

        user_id = User.decode_auth_token(auth_token)

        user = User.objects.get(id=user_id)

        if user:

            if request.method == 'PUT':

                post_data = json.loads(request.body.decode())

                params = ['distance', 'price_min',
                          'price_max', 'rating_min', 'rating_max']

                for param in params:

                    if param in user.preference.__dict__:

                        user.preference.__dict__[param] = post_data.get(
                            param, user.preference.__dict__[param])

                for genre in post_data.get('food_genre'):

                    user.preference.food_genre.append(genre)

                temp = list(set(user.preference.food_genre))

                if '' in temp:

                    temp.remove('')

                user.preference.food_genre = temp

                user.preference.save()

                responseObject = {
                    'status': HTTP_200_OK,
                    'message': 'User preference successfully updated.',
                }

                return JsonResponse(responseObject)

            else:

                responseObject = {
                    'status': HTTP_405_METHOD_NOT_ALLOWED,
                    'message': 'Only PUT requests are allowed'
                }

                return JsonResponse(responseObject)

        else:

            responseObject = {
                'status': HTTP_401_UNAUTHORIZED,
                'message': 'Invalid authorization token'
            }

            return JsonResponse(responseObject)
    else:

        responseObject = {
            'status': HTTP_401_UNAUTHORIZED,
            'message': 'No authorized token given'
        }

        return JsonResponse(responseObject)


@csrf_exempt
def user_preferences(request):

    if request.META['HTTP_AUTHORIZATION']:

        auth_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]

        user_id = User.decode_auth_token(auth_token)

        user = User.objects.get(id=user_id)

        if user:

            data = json.loads(serializers.serialize(
                'json', [user.preference]))[0]['fields']

            del data['user']

            return JsonResponse(data)

        else:

            responseObject = {
                'status': HTTP_401_UNAUTHORIZED,
                'message': 'No authorized token given'
            }

            return JsonResponse(responseObject)

    else:
        responseObject = {
            'status': HTTP_401_UNAUTHORIZED,
            'message': 'Invalid authorization token'
        }

        return JsonResponse(responseObject)
