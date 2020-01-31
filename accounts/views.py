from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Profile
from .serializers import UserSerializer, ProfileSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def get_friends(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        friends = profile.friends.all()
        serializer = UserSerializer(friends, many=True)
        return JSONResponse(serializer.data)

def get_profile_data(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile, many=False)
        return JSONResponse(serializer.data)

def check_user_exists(request, username):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user, many=False)
            return JSONResponse(serializer.data)
        except User.DoesNotExist:
            return JSONResponse(
                {
                    'error': 'User does NOT exists.',
                    'error_code': 'E001'
                }
            )
        
