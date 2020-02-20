from django.urls import path
from . import views

urlpatterns = [
    path(r'friends/<username>/', views.get_friends, name='friends_list'),
    path(r'groups/', views.get_groups, name='groups_list'),
    path(r'profile/un/', views.get_profile_data, name='user_profile'),
    path(r'profile/ph/', views.get_profile_data_by_phone, name='user_profile_by_phone'),
    path(r'add_friend/', views.add_friend, name='add_friend'),

    path(r'create_user/', views.create_user, name='create_user'),
]
