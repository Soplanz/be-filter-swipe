from django.db import models
from django.contrib.auth.models import User

class Like(models.Model):
    user_id = models.IntegerField(null=True, default=None)
    liked_user_id = models.IntegerField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

class Dislike(models.Model):
    user_id = models.IntegerField(null=True, default=None)
    disliked_user_id = models.IntegerField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.IntegerField(null=True, default=None)
    message = models.TextField(null=True, default='Uninitialized text')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message