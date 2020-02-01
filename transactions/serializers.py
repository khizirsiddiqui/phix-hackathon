from .models import Transaction
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'amount',
            'txn_id',
            'source',
            'destination',
            'txn_type',
            'status',
            'currency',
            'txn_date_time',
            'description')
