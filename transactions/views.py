from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import datetime, timedelta

from accounts.models import Profile
from .models import Transaction
from .serializers import TransactionSerializer
from .utils import last_day_of_month

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def transaction_list(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        transactions = user.profile.all_transactions()
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

def user_transaction_list(request, txn_type):
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
        profile = Profile.objects.get(user=user)
        transactions = profile.get_all_specific(txn_type=txn_type)
        serializer = TransactionSerializer(transactions, many=True)
        return JSONResponse(serializer.data)

def user_today_transactions(request):
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

def get_home_activity_analytics_data(request):
    if request.GET:
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
        analytics = {}

        num_days_left = (last_day_of_month(datetime.today()) - datetime.today()).days
        num_days_this_month = datetime.today().day
        dnames = {'0':'today', '7':'week', '31':'month', str(num_days_this_month):'this_month'}
        for dlen in (0, 7, 31, num_days_this_month):
            txn_set = user.profile.get_analytic_transactions(dlen)
            analytics[dnames[str(dlen)]] = 0
            for txn in txn_set:
                amount = int(txn.amount)
                if txn.txn_type == 0:
                    # IF debit
                    amount = amount * -1.
                analytics[dnames[str(dlen)]] += amount
        analytics['daily_avg_current'] = int(analytics['this_month'])/num_days_this_month
        analytics['daily_avg_required'] = int(user.profile.monthly_stipend - analytics['this_month'])/num_days_left
        analytics['days_remaining'] = num_days_left

        return JSONResponse(analytics)

def get_analytics(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JSONResponse(
            {
                'error': 'User does NOT exists.',
                'error_code': 'E001'
            }
        )
    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(0, 30)]
    analytics = {}
    for dateX in date_list:
        txn_set = user.profile.get_transactions_on(dateX)
        analytics[dateX.day] = 0
        for txn in txn_set:
            amount = int(txn.amount)
            if txn.txn_type == 0:
                # IF debit
                amount = amount * -1.
        analytics[dateX.day] += amount
    stats = {}
    num_days_left = (last_day_of_month(datetime.today()) - datetime.today()).days
    num_days_this_month = datetime.today().day
    dnames = {'0':'today', '7':'week', '31':'month', str(num_days_this_month):'this_month'}
    for dlen in (0, 7, 31, num_days_this_month):
        txn_set = user.profile.get_analytic_transactions(dlen)
        stats[dnames[str(dlen)]] = 0
        for txn in txn_set:
            amount = int(txn.amount)
            if txn.txn_type == 0:
                # IF debit
                amount = amount * -1.
            stats[dnames[str(dlen)]] += amount
    stats['daily_avg_current'] = int(stats['this_month'])/num_days_this_month
    stats['daily_avg_required'] = int(user.profile.monthly_stipend - stats['this_month'])/num_days_left
    stats['days_remaining'] = num_days_left
    return JSONResponse({
        "data": analytics,
        'stats': stats
    })

def get_outstanding(request, source, destination):
    if request.method == 'GET':
        user = get_object_or_404(User, username=source)
        second_user = get_object_or_404(User, username=destination)
        txn_set = user.profile.all_P2P_transactions(second_user)
        total_amount = 0
        for txn in txn_set:
            amount = int(txn.amount)
            if txn.txn_type == 0:
                # IF debit
                amount = amount * -1
            total_amount += amount
        return JSONResponse({
            'amount': total_amount
        })

@api_view(['POST'])
def settle_up(request, source, destination):
    if request.method == 'POST':
        user = get_object_or_404(User, username=source)
        second_user = get_object_or_404(User, username=destination)
        txn_type_dict = {'debit':0, 'credit':1}
        transaction = Transaction.objects.create(
            source=user,
            destination=destination,
            txn_date_time=datetime.now,
            status='processed',
            description=request.POST['description'],
            txn_id=request.POST['txn_id'],
            txn_type=txn_type_dict[request.POST['txn_id']]
        )
        return JSONResponse(TransactionSerializer(transaction).data)


class TransactionAPIView(APIView):
    def post(self, request, format=None):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
