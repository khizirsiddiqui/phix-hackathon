from django.contrib import admin
from transactions.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "amount", "txn_id", "txn_date_time")
