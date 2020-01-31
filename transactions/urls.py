from django.urls import path
from . import views

urlpatterns = [
    path(r'debits/<username>/', views.user_transaction_list, name='debit_list', kwargs={'txn_type': 0}),
    path(r'credits/<username>/', views.user_transaction_list, name='credit_list', kwargs={'txn_type': 1}),
    path(r'create_transaction/', views.create_transaction, name='create_transaction'),
]
