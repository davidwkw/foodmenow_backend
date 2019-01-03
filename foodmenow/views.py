import requests
import json
import re
import pickle
from django.core import serializers
from django.http import JsonResponse, HttpResponse, QueryDict
from foodmenow.models import User, Preference
from food_me_now_backend.settings import YELP_SECRET_KEY, UBER_CLIENT_ID, UBER_CLIENT_SECRET
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED
)
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient
from uber_rides.errors import ClientError, ServerError, UberIllegalState
from uber_rides.session import Session, OAuth2Credential

# APIs


@csrf_exempt
def restaurant_search(request):

    if request.META.get('HTTP_AUTHORIZATION', False):

        auth_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]

        user_id = User.decode_auth_token(auth_token)

        user = User.objects.get(id=user_id)

        if user:

            category_list = [", ".join(user.preference.food_genre)]

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

        payload = {'latitude': request.GET['latitude'],
                   'longitude': request.GET['longitude'],
                   'radius': request.GET.get('radius', ''),
                   'price': request.GET.get('price', ''),
                   'categories': request.GET.get('categories', ''),
                   'term': ['restaurants', 'food'],
                   'limit': 25,
                   }

        r = requests.get('https://api.yelp.com/v3/businesses/search',
                         params=payload, headers={'Authorization': f'Bearer {YELP_SECRET_KEY}'})

        data = r.json()

        return JsonResponse(data)


@csrf_exempt
def restaurant_reviews(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}/reviews/', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)


@csrf_exempt
def restaurant_details(request, id):

    r = requests.get(f'https://api.yelp.com/v3/businesses/{id}', headers={
        'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)


@csrf_exempt
def uber_request(request):

    if request.method == 'POST':

        auth_flow = AuthorizationCodeGrant(
            UBER_CLIENT_ID,
            {'request'},
            UBER_CLIENT_SECRET,
            'https://react-foodme.herokuapp.com/restaurant',
        )

        try:

            post_data = json.loads(request.body.decode())

        except:

            auth_url = auth_flow.get_authorization_url()

            return JsonResponse({'authentication_url': auth_url})

        if post_data.get('uber_user_credentials', False):

            uber_user_credentials = post_data.get('uber_user_credentials')

            credentials = OAuth2Credential(
                UBER_CLIENT_ID,
                uber_user_credentials['access_token'],
                uber_user_credentials['expires_in_seconds'],
                set(uber_user_credentials['scopes']),
                'authorization_code',
                'https://react-foodme.herokuapp.com/restaurant',
                UBER_CLIENT_SECRET,
                uber_user_credentials['refresh_token']
            )

            session = Session(oauth2credential=credentials)
            client = UberRidesClient(session, sandbox_mode=True)

            try:
                product_id = post_data['product_id']

            except:

                pass

            try:

                request_id = post_data['request_id']

            except:

                pass

            if post_data.get('cancel_ride', False) and post_data.get('ride_details', False) and post_data.get('get_estimate', False) and post_data.get('display_products', False):

                response = client.cancel_ride(request_id)

                ride = response.json

                return JsonResponse(ride, safe=False)

            elif post_data.get('ride_details', False) and post_data.get('get_estimate', False) and post_data.get('display_products', False):

                response = client.get_ride_details(request_id)

                ride = response.json

                return JsonResponse(ride)

            elif post_data.get('request_ride', False) and post_data.get('get_estimate', False) and post_data.get('display_products', False):

                response = client.request_ride(
                    product_id=product_id,
                    start_latitude=post_data['current_latitude'],
                    start_longitude=post_data['current_longitude'],
                    end_latitude=post_data['destination_latitude'],
                    end_longitude=post_data['destination_longitude'],
                    seat_count=post_data['passenger_amt'],
                    fare_id=post_data['fare_id']
                )

                request = response.json
                request_id = request.get('request_id')

                return JsonResponse(request_id, safe=False)

            elif post_data.get('get_estimate', False) and post_data.get('display_products', False):

                estimate = client.estimate_ride(
                    product_id=product_id,
                    start_latitude=post_data['current_latitude'],
                    start_longitude=post_data['current_longitude'],
                    end_latitude=post_data['destination_latitude'],
                    end_longitude=post_data['destination_longitude'],
                    seat_count=post_data['passenger_amt']
                )

                fare = estimate.json.get('fare')

                return JsonResponse(fare, safe=False)

            elif post_data.get('display_products', False):

                response = client.get_products(
                    post_data['current_latitude'], post_data['current_longitude'])

                products = response.json.get('products')

                return JsonResponse(products, safe=False)

            else:

                return JsonResponse({"message": "Please input either display_products, get_estimate, request_ride, ride_details or cancel_ride as boolean value to proceed or ensure that each item is set to true in ascending order"})

        elif post_data.get('uber_code_url', False):

            result = post_data['uber_code_url'].strip()

            state = re.search("^.*\?code=.*state=(.*)#_$", result).group(1)

            auth_flow = AuthorizationCodeGrant(
                UBER_CLIENT_ID,
                {'request'},
                UBER_CLIENT_SECRET,
                'https://react-foodme.herokuapp.com/restaurant',
                state
            )

            try:

                session = auth_flow.get_session(result)
                credentials = session.oauth2credential

                x = {'scopes': list(credentials.__dict__['scopes'])}

                credentials.__dict__.update(x)

                data = {"uber_user_credentials":
                        {
                            "access_token": credentials.__dict__['access_token'],
                            "expires_in_seconds": credentials.__dict__['expires_in_seconds'],
                            "scopes": credentials.__dict__['scopes'],
                            "refresh_token": credentials.__dict__['refresh_token']
                        }
                        }

                return JsonResponse(data)

            except (ClientError, UberIllegalState) as error:

                return HttpResponse(error)

        else:

            responseObject = {
                'status': HTTP_401_UNAUTHORIZED,
                'message': 'Either redirect code URI or Uber user credentials required'
            }

            return JsonResponse(responseObject)

    else:

        responseObject = {
            'status': HTTP_405_METHOD_NOT_ALLOWED,
            'message': 'Only POST requests are allowed'
        }

        return JsonResponse(responseObject)

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

    if request.META.get('HTTP_AUTHORIZATION', False):

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

    if request.META.get('HTTP_AUTHORIZATION', False):

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
