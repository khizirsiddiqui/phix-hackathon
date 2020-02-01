from django.contrib import admin
from accounts.models import Profile, Group

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "upi_id")

admin.site.register(Group)
