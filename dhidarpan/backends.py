from typing import Any
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest
from blog.models import ProfileInfo

class EmailBackend(ModelBackend):
    def authenticate(self, request, email, username=None, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        pinstance = ProfileInfo.objects.get(user_id=get_user_model().objects.get(email=user.email).id)
        if pinstance.isGoogleUser:
            return user
        return None