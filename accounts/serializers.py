from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    upi_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'get_full_name',
            'image_url',
            'upi_id')
    
    def get_image_url(self, user):
        profile = Profile.objects.get(user=user)
        request = self.context.get("request")
        photo_url = profile.image.url
        return request.build_absolute_uri(photo_url)

    def get_upi_id(self, user):
        profile = Profile.objects.get(user=user)
        return profile.upi_id

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
