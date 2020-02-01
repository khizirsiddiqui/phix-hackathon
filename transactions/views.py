from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from accounts.models import Profile
from .models import Transaction
from .serializers import TransactionSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def transaction_list(request):
    if request.method == 'GET':
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

def user_transaction_list(request, username, txn_type):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        transactions = profile.get_all_specific(txn_type=txn_type)
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

def user_today_transactions(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        transactions = profile.get_today_transactions()
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

def all_P2P_transactions(request, username1, username2):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username1)
        profile = Profile.objects.get(user=user)
        second_user = get_object_or_404(User, username=username2)
        transactions = profile.all_P2P_transactions(second_user)
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

class TransactionAPIView(APIView):
    def post(self, request, format=None):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
