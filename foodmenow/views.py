from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
import json
from food_me_now_backend.settings import YELP_SECRET_KEY
from foodmenow.models import User, Preference
# Create your views here.


def restaurant_search(request, latitude, longitude, radius, price, categories):

    params = {'latitude': latitude,
              'longitude': longitude,
              'term': 'restaurants',
              'radius': radius,
              'price': price,
              'categories': categories}

    import pdb
    pdb.set_trace()

    r = requests.get('https://api.yelp.com/v3/businesses/search',
                     params=params, headers={'Authorization': f'Bearer {YELP_SECRET_KEY}'})

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


def create_user(request):

    if request.method == 'POST':

        post_data = request.content_params

        new_user = User(email=post_data.get('email'),
                        password_hash=User.set_password(
                            post_data.get('password')),
                        username=post_data.get('username'))

        new_user.save()

    return HttpResponse('User successfully created')


# def login_user(request):

#     if request.method == 'POST':
#         post_data = request.content_params
