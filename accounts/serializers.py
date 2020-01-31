from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'get_full_name',
            'image_url')
    
    def get_image_url(self, user):
        profile = Profile.objects.get(user=user)
        request = self.context.get("request")
        # photo_url = profile.image.url
        return request

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'user',
            'total_expense',
            'monthly_stipend',
            'active',
            'friends',
            'image')
