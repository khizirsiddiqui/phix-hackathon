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
    if request.POST:
        error = None
        error_msg = ''
        if request.POST:
            try:
                source = User.objects.get(username=source)
            except User.DoesNotExist:
                error = 'E001'
                error_msg = 'User does Not exists.'
                return JSONResponse({
                    'error': error,
                    'error_msg': error_msg
                })

            if destination is not None:
                destination = get_object_or_404(User, username=destination)

            try:
                amount = float(amount)
            except ValueError:
                error = 'E011'
                error_msg = 'Invalid Amount ' + str(amount)
                return JSONResponse({
                    'error': error,
                    'error_msg': error_msg
                })

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
            serializer = TransactionSerializer(txn_obj, many=False)
            return JSONResponse(serializer.data)
    return JSONResponse({
        'error': 'E101',
        'error_msg': 'ONlY POST REQUEST ACCEPTED.'
    })
