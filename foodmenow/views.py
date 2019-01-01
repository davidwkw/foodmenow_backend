import requests
import json
import re
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

# Create your views here.

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
                   'term': 'restaurants',
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


# @csrf_exempt
# def uber_request(request):

#     auth_flow = AuthorizationCodeGrant(
#         UBER_CLIENT_ID,
#         ['request'],
#         UBER_CLIENT_SECRET,
#         'http://localhost:8000/uber/request/'
#     )

#     try:

#         post_data = json.loads(request.body.decode())

#     except:

#         auth_url = auth_flow.get_authorization_url()

#         return JsonResponse({'authentication_url': auth_url})

#     if post_data.get('uber_code_url', False):

#         result = post_data['uber_code_url'].strip()

#         uber_code = re.search("^.*\?code=(.*)$", result).group(1)

#         uber_req = {
#             'client_secret': (None, UBER_CLIENT_SECRET),
#             'client_id': (None, UBER_CLIENT_ID),
#             'code': (None, uber_code),
#             'scope': (None, 'request'),
#             'grant_type': (None, 'authorization_code'),
#             'redirect_uri': (None, 'http://localhost:8000/uber/request/')
#         }

#         result = requests.post(
#             'https://login.uber.com/oauth/v2/token', files=uber_req)

#         import pdb
#         pdb.set_trace()
#     else:

#         return HttpResponse('Uber code URL required')


@csrf_exempt
def uber_request(request):

    auth_flow = AuthorizationCodeGrant(
        UBER_CLIENT_ID,
        {'request'},
        UBER_CLIENT_SECRET,
        'http://localhost:8000/uber/request/',
    )

    try:

        post_data = json.loads(request.body.decode())

    except:

        auth_url = auth_flow.get_authorization_url()

        return JsonResponse({'authentication_url': auth_url})

    if post_data.get('uber_code_url', False):

        result = post_data['uber_code_url'].strip()

        state = re.search("^.*\?code=.*state=(.*)#_$", result).group(1)

        auth_flow = AuthorizationCodeGrant(
            UBER_CLIENT_ID,
            {'request'},
            UBER_CLIENT_SECRET,
            'http://localhost:8000/uber/request/',
            state
        )

        try:
            session = auth_flow.get_session(result)
            client = UberRidesClient(session, sandbox_mode=True)
            credentials = session.oauth2credential

        except (ClientError, UberIllegalState) as error:

            return HttpResponse(error)

        response = client.get_products(
            post_data['current_latitude'], post_data['current_longitude'])

        products = response.json.get('products')

        product_id = products[0].get('product_id')

        estimate = client.estimate_ride(
            product_id=product_id,
            start_latitude=post_data['current_latitude'],
            start_longitude=post_data['current_longitude'],
            end_latitude=post_data['destination_latitude'],
            end_longitude=post_data['destination_logitude'],
            seat_count=post_data['passenger_amt']
        )

        fare = estimate.json.get('fare')

        response = client.request_ride(
            product_id=product_id,
            start_latitude=post_data['current_latitude'],
            start_longitude=post_data['current_longitude'],
            end_latitude=post_data['destination_latitude'],
            end_longitude=post_data['destination_logitude'],
            seat_count=post_data['passenger_amt'],
            fare_id=fare['fare_id']
        )

        request = response.json
        request_id = request.get('request_id')

        return HttpResponse('Success')

    else:

        return HttpResponse('Uber code URL required')


@csrf_exempt
def uber_call(request):

    if request.method == 'POST':

        post_data = json.loads(request.body.decode())

        payload = {
            'fare_id': request.POST['fare_id'],
            'start_latitude': request.POST['current_latitude'],
            'start_longitude': request.POST['current_longitude'],
            'end_latitude': request.POST['destination_latitude'],
            'end_longitude': request.POST['destination_logitude']
        }

        r = requests.post(
            'https://sandbox-api.uber.com/v1.2/requests', json=payload
        )

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

        import pdb
        pdb.set_trace()

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
