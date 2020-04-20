from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

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
        groups = user.profile.group.all()
        serializer = GroupSerializer(groups, many=True,)
        return JSONResponse(serializer.data)

@api_view(['GET'])
def get_profile_data(request):
    user = User.objects.filter(username__iexact=request.GET['keyword']).first()
    if user is None:
        profile = Profile.objects.filter(phone_number__contains=request.GET['keyword']).first()
    else:
        profile = Profile.objects.get(user=user)
    serializer = ProfileSerializer(profile, many=False, context={"request": request})
    return Response(serializer.data, status=status.HTTP_302_FOUND)

def check_user_exists(username):
    return User.objects.filter(username=username).count() > 0

@api_view(['POST'])
def add_friend(request):
    if 'friend_username' not in request.POST:
        return Response(
            {
                'error': 'friend_username not found.',
                'error_code': 'E007'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )
    if 'username' not in request.POST:
        return Response(
            {
                'error': 'username not found.',
                'error_code': 'E008'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )

    if check_user_exists(request.POST['friend_username']):
        friend = get_object_or_404(User, username=request.POST['friend_username'])
        user = get_object_or_404(User, username=request.POST['username'])
        user.profile.friends.add(friend)
        user.profile.save()
        friends = user.profile.friends.all()
        serializer = UserSerializer(friends, many=True, context={"request": request})
        return JSONResponse(serializer.data)
    else:
        return JSONResponse(
            {
                'error': 'User does NOT exists.',
                'error_code': 'E001'
            }
        )

@csrf_exempt
@api_view(['POST'])
def create_user(request):
    if 'email' not in request.POST:
        return Response(
            {
                'error': 'Invalid Email ID.',
                'error_code': 'E003'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )
    email = request.POST['email']
    username = ''
    if ('@' in email):
        username = email.split('@')[0]
    else:
        return Response(
            {
                'error': 'Invalid Email ID.',
                'error_code': 'E003'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )
    if check_user_exists(username):
        return Response(
            {
                'error': 'User already exists.',
                'error_code': 'E002'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )
    if 'get_full_name' not in request.POST:
        return Response(
            {
                'error': 'Can not create account without Name.',
                'error_code': 'E004'
            },
            status=status.HTTP_206_PARTIAL_CONTENT
        )
    full_name = request.POST['get_full_name']
    first_name, last_name = full_name.split()
    if 'upi_id' not in request.POST:
        return Response({
                'error_code': 'E005',
                'error': 'Can not create account without UPI ID.'
            },
            status=status.HTTP_206_PARTIAL_CONTENT)
    if 'image_string' not in request.POST:
        return JSONResponse({
                'error_code': 'E006',
                'error': 'Can not create account without Image.'
            },
            status=status.HTTP_206_PARTIAL_CONTENT)
    
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
