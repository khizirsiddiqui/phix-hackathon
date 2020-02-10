from django.urls import path
from . import views

urlpatterns = [
    path(r'friends/<username>/', views.get_friends, name='friends_list'),
    path(r'groups/', views.get_groups, name='groups_list'),
    path(r'profile/<username>/', views.get_profile_data, name='user_profile'),
    path(r'profile/ph/<phone_number>/', views.get_profile_data_by_phone, name='user_profile_by_phone'),
    path(r'friend/<username>/<friend_username>/', views.add_friend, name='friend_add'),

    path(r'create_user/', views.create_user, name='create_user'),
]
