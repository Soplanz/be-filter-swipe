from rest_framework.decorators import api_view
from rest_framework.response import Response
import pika
from .models import Like, Dislike, Notification
from .serializers import LikeSerializer, DislikeSerializer

from django.db.models import Q
import requests, json

URL_VERIFY = 'http://34.70.123.231:3001/auth/profile'
URL_PROFILE = 'http://34.70.123.231/api/profile/'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
channel = connection.channel()

def send_notification(like):
    channel.basic_publish(
        exchange='', 
        routing_key='notifications', 
        body=json.dumps({
            "user_id": f"{like.user_id}", 
            "target_id": f"{like.liked_user_id}", 
            "message": f"{like.liked_user_id} have a new like from {like.user_id}.",
            "match": False})
    )

def send_notification_bidirectional(user_id, target_id):
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps({
            "user_id": f'{user_id}', 
            "target_id": f"{target_id}", 
            "message": f"{user_id} and {target_id} have liked each other!", 
            "match": True})
    )

@api_view(['POST'])
def like(request, target_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'error': f'Authentication failed token not found'}, status=401)
    
    headers = {'Authorization': token}
    check_valid = requests.get(URL_VERIFY, headers=headers)
    if check_valid.status_code == 200:
        response      = requests.get(URL_PROFILE + "get_my_profile/", headers=headers)
        user_response = requests.get(URL_PROFILE + target_id, headers=headers)
        response_data = response.json()

        user_data     = user_response.json()
        user_id       = response_data['id']

        if int(user_id) == int(target_id):
            return Response({'error': f'Liked user and liker cannot be the same'}, status=500)
    
        like = Like(user_id=user_id, liked_user_id=target_id)
        like.save()

        serialized_data = LikeSerializer(like).data
        Notification.objects.create(
            user=target_id,
            message=f"You have a new like from {user_id}."
        )
        send_notification(like) 

        # Assume that user id is always same as the request user id
        if Like.objects.filter(Q(user_id=target_id) & Q(liked_user_id=user_id)).exists():

            data = json.dumps({'username': f"{user_data['user']['username']}"})
            headers['Content-Type'] = 'application/json'
            add_teman_response = requests.post(URL_PROFILE+'add_teman/', headers=headers, data=data)
            
            if add_teman_response.status_code == 200:
                Notification.objects.create(
                    user=target_id,
                    message=f"You and {user_id} have liked each other!"
                )
                Notification.objects.create(
                    user=user_id,
                    message=f"You and {target_id} have liked each other!."
                )
                send_notification_bidirectional(user_id, target_id)

        return Response(serialized_data, content_type='application/json')
    else:
        return Response({'error': f'An error occured with code {check_valid.status_code}'}, status=check_valid.status_code)


@api_view(['POST'])
def dislike(request, target_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'error': f'Authentication failed token not found'}, status=401)
    headers = {'Authorization': token}
    check_valid = requests.get(URL_VERIFY, headers=headers)
    if check_valid.status_code == 200:
        response_data = requests.get(URL_PROFILE + "get_my_profile/", headers=headers).json()
        user_id       = response_data['id']
        
        if int(user_id) == int(target_id):
            return Response({'error': f'Disliked user and disliker cannot be the same'}, status=500)

        dislike = Dislike(user_id=user_id, disliked_user_id=target_id)
        dislike.save()
        serialized_data = DislikeSerializer(dislike).data
        return Response(serialized_data, content_type='application/json')
    else:
        return Response({'error': f'An error occured with code {check_valid.status_code}'}, status=check_valid.status_code)


@api_view(['GET'])
def get_dislikes(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'error': f'Authentication failed token not found'}, status=401)
    
    headers = {'Authorization': token}
    check_valid = requests.get(URL_VERIFY, headers=headers)

    if check_valid.status_code == 200:
        response_data   = requests.get(URL_PROFILE + "get_my_profile/", headers=headers).json()
        user_id         = response_data['id']
        dislikes_data   = Dislike.objects.filter(Q(user_id=user_id))
        serialized_data = DislikeSerializer(dislikes_data, many=True).data
        return Response(serialized_data, content_type='application/json')
    else:
        return Response({'error': f'An error occured with code {check_valid.status_code}'}, status=check_valid.status_code)


@api_view(['GET'])
def get_likes(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'error': f'Authentication failed token not found'}, status=401)
    
    headers = {'Authorization': token}
    check_valid = requests.get(URL_VERIFY, headers=headers)

    if check_valid.status_code == 200:
        response_data   = requests.get(URL_PROFILE + "get_my_profile/", headers=headers).json()
        user_id         = response_data['id']
        likes_data      = Like.objects.filter(Q(user_id=user_id))
        serialized_data = LikeSerializer(likes_data, many=True).data
        return Response(serialized_data, content_type='application/json')
    else:
        return Response({'error': f'An error occured with code {check_valid.status_code}'}, status=check_valid.status_code)