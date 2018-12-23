from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# from food_me_now_backend.settings import YELP_SECRET_KEY
import requests, json
from food_me_now_backend.settings import YELP_SECRET_KEY

# Create your views here.

def restaurant_search(request, latitude, longitude, radius, price, categories):

    params = {'latitude' : latitude,
            'longitude' : longitude,
            'term' : 'restaurants',
            'radius' : radius,
            'price' : price,
            'categories' : categories }

    r = requests.get('https://api.yelp.com/v3/businesses/search', params=params, headers={'Authorization': f'Bearer {YELP_SECRET_KEY}'})

    data = r.json()

    return JsonResponse(data)