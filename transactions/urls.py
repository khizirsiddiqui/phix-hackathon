from django.urls import path
from . import views

urlpatterns = [
    path(r'all_transaction/', views.transaction_list, name='transaction_list'),

    path(r'debits/<username>/', views.user_transaction_list, name='debit_list', kwargs={'txn_type': 0}),
    path(r'credits/<username>/', views.user_transaction_list, name='credit_list', kwargs={'txn_type': 1}),

    path(r'today_transactions/<username>/', views.user_today_transactions, name='user_today_transactions'),
    path(r'transactions/<username1>/<username2>', views.all_P2P_transactions, name='all_P2P_transactions'),

    path(r'create_transaction/', views.TransactionAPIView.as_view(), name='create_transaction'),
]
