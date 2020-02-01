from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Profile, Group
from .serializers import UserSerializer, ProfileSerializer, CreateUserSerializer, GroupSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

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
        friends = user.profile.friends.all()
        serializer = UserSerializer(friends, many=True, context={"request": request})
        return JSONResponse(serializer.data)

def get_groups(request):
    if request.method == 'GET':
        if not 'username' in request.GET:
            return JSONResponse({
                'error_code': 'E007',
                'error': 'Please provide a valid username'
            })
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JSONResponse(
                {
                    'error': 'User does NOT exists.',
                    'error_code': 'E001'
                }
            )
        print(user)
        groups = user.profile.group.all()
        print(groups)
        serializer = GroupSerializer(groups, many=True,)
        return JSONResponse(serializer.data)

def get_profile_data(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile, many=False, context={"request": request})
        return JSONResponse(serializer.data)

def check_user_exists(username):
    return User.objects.filter(username=username).count() > 0

def check_user_exists_api(request, username):
    if request.method == 'GET':
        if check_user_exists(username):
            user = User.objects.get(username=username)
            serializer = UserSerializer(user, many=False, context={"request": request})
            return JSONResponse(serializer.data)
        else:
            return JSONResponse(
                {
                    'error': 'User does NOT exists.',
                    'error_code': 'E001'
                }
            )

@api_view(['POST'])
def create_user(request):
    if request.POST:
        if 'email' not in request.POST:
            return JSONResponse(
                {
                    'error': 'Invalid Email ID.',
                    'error_code': 'E003'
                }
            )
        email = request.POST['email']
        username = ''
        if ('@' in email):
            username = email.split('@')[0]
        else:
            return JSONResponse(
                {
                    'error': 'Invalid Email ID.',
                    'error_code': 'E003'
                }
            )
        if check_user_exists(username):
            return JSONResponse(
                {
                    'error': 'User already exists.',
                    'error_code': 'E002'
                }
            )
        if 'full_name' not in request.POST:
            return JSONResponse(
                {
                    'error': 'Can not create account without Name.',
                    'error_code': 'E004'
                }
            )
        full_name = request.POST['full_name']
        first_name, last_name = full_name.split()
        if 'upi_id' not in request.POST:
            return JSONResponse({
                'error_code': 'E005',
                'error': 'Can not create account without UPI ID.'
            })
        if 'image_string' not in request.POST:
            return JSONResponse({
                'error_code': 'E006',
                'err*or': 'Can not create account without Image.'
            })
        
        user_data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        user_serializer = CreateUserSerializer(data=user_data)
        if user_serializer.is_valid():
            instance = user_serializer.save()
            profile = Profile.objects.get(user=instance)
            profile.upi_id = request.POST['upi_id']
            profile.total_expense = request.POST.get('total_expense', 0)
            profile.monthly_stipend = request.POST.get('monthly_stipend', 0)
            profile.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
