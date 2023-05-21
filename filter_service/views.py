from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from swipe_service.models import Dislike
from django.db.models import Q

import requests
import json

IP_ADDRESS_PROFILE = 'localhost:8000'
endpoint_url = f'http://{IP_ADDRESS_PROFILE}/api/profile/'


@api_view(['GET'])
def profile_list(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'error': f'Authentication failed token not found'}, status=401)

    hobi = str(request.GET.get('hobi', '')) 
    genre = str(request.GET.get('genre', ''))
    gender = str(request.GET.get('gender', ''))
    age_range = str(request.GET.get('age_range', ''))
    domisili = str(request.GET.get('domisili', ''))

    min_age = 0
    max_age = 200

    if age_range != '':
        raw_age = str(age_range).split('-')
        min_age = int(raw_age[0])
        max_age = int(raw_age[1])

    headers = {'Authorization': token}
    response = requests.get(endpoint_url, headers=headers)
    
    if response.status_code == 200:
        my_data  = requests.get(endpoint_url + 'get_my_profile/', headers=headers).json()
        user_id  = my_data['id']
        profiles = response.json()
        friend   = requests.get(endpoint_url+'get_my_friend', headers=headers).json()

        filtered_profiles = []
        for profile in profiles:
            if (profile['umur'] is None or (min_age <= profile['umur'] <= max_age)) \
            and (not genre or any(str(data.get('genre')) == genre for data in profile.get('genre', [])))\
            and (not gender or str(profile.get('gender', None)) == gender)\
            and (not domisili or str(profile.get('domisili', None)) == domisili)\
            and (not hobi or any(str(data.get('hobi')) == hobi for data in profile.get('hobi', [])))\
            and profile['user']['username'] not in [data['username'] for data in friend]\
            and not Dislike.objects.filter(user_id=user_id, disliked_user_id=profile['id']).exists():
                filtered_profiles.append(profile)
            
        return Response(filtered_profiles, content_type='application/json')
    else:
        return Response({'error': f'Failed to fetch data {response.status_code}'}, status=response.status_code)
