from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
import json

# Create your views here.

def bussiness_search(request):
    params = {'location' : 'New York City'}
    
    r = requests.get('https://api.yelp.com/v3/businesses/search', params=params, headers={'Authorization': 'Bearer 53OigNCghYI1KMt3ESL-dBZRemhUA9QjxuNlu_nm8Mx7bkFJLrET_hqMYMKIG4RzQH8YXTwx1JRJWCqKiBXjZldqo8RoSAIO5_yUFWYFuqPenK8biBV4MSAcQ60YXHYx'})

    print(type(r))

    data = r.json()

    import pdb; pdb.set_trace()
    print(type(data))
    
    return JsonResponse(r)