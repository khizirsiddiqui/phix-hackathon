from django.urls import path
from . import views

urlpatterns = [
    path(r'friends/<username>/', views.get_friends, name='friends_list'),
    path(r'profile/<username>/', views.get_profile_data, name='user_profile'),
    path(r'check/<username>/', views.check_user_exists, name='check_user_exists'),
]