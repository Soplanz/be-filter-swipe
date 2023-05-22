from django.urls import path
from .views import like, dislike, get_likes, get_dislikes

urlpatterns = [
    path('like/<target_id>', like, name='like'),
    path('dislike/<target_id>', dislike, name='dislike'),
    path('get_likes', get_likes, name='likes'),
    path('get_dislikes', get_dislikes, name='dislikes'),
]