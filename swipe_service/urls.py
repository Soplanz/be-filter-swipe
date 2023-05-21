from django.urls import path
from .views import like, dislike

urlpatterns = [
    path('like/<target_id>', like, name='like'),
    path('dislike/<target_id>', dislike, name='dislike'),
]