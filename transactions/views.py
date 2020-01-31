from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
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

def create_transaction(request,
                       amount,
                       source,
                       destination,
                       txn_type,
                       description,
                       txn_id,
                       status,
                       txn_date_time):
    error = False
    error_msg = ''
    if request.POST:
        source = get_object_or_404(User, username=source)
        source_profile = Profile.objects.get(user=source)
        
        if destination is not None:
            destination = get_object_or_404(User, username=destination)
            destination_profile = Profile.objects.get(user=destination)
        
        try:
            amount = float(amount)
        except ValueError:
            error = True
            error_msg = 'Invalid Amount ' + str(amount)
        
        if txn_date_time is None:
            txn_date_time = datetime.now
        
        txn_obj = Transaction.objects.create(
            amount=amount,
            txn_id=txn_id,
            description=description,
            destination=destination,
            txn_type=txn_type,
            status=status,
            txn_date_time=txn_date_time
        )
        return "Hello"
        
