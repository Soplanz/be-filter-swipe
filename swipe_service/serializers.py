from rest_framework import serializers
from .models import Like, Dislike

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user_id', 'liked_user_id', 'created_at')

class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = ('id', 'user_id', 'disliked_user_id', 'created_at')