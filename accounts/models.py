from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from django.utils.timezone import make_aware

from phix import settings
from .utils import image_as_base64
from .validators import validate_upi_id
from transactions.models import Transaction

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from datetime import datetime, date, time, timedelta


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = ProcessedImageField(upload_to='avatar',
                           processors=[ResizeToFill(60, 60)],
                           format='JPEG',
                           options={'quality': 60})
    total_expense = models.FloatField("Total Expenses", default=0)
    monthly_stipend = models.FloatField("Monthly Expense", default=0)
    active = models.BooleanField("Active Account", default=True)
    currency = models.CharField("Currency", default="INR", max_length=5)
    friends = models.ManyToManyField(User, related_name="friends")
    upi_id = models.CharField("UPI ID", max_length=100, default="example@upi", validators=[validate_upi_id])

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        managed = True
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def get_cover_base64(self):
        # How to Use:
        # <img src="{{ post.get_cover_base64 }}">
        return image_as_base64(settings.MEDIA_ROOT + self.image.path)
    
    def get_all_specific(self, from_date=None, to_date=None, second_user=None, txn_type=1):
        if from_date is None:
            # This is a random date before which no txn could have been recorded.
            from_date = make_aware(datetime(2000, 1, 1, 0, 0, 1))
        if to_date is None:
            to_date = make_aware(datetime.now())
        transactions = Transaction.objects.filter(
            (Q(txn_type=txn_type) & Q(destination=second_user) & Q(source=self.user)) | 
            (Q(txn_type=(not txn_type)) & Q(source=second_user) & Q(destination=self.user)),
            txn_date_time__range=[
                from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date.strftime("%Y-%m-%d %H:%M:%S")],
        )
        return transactions

    def get_analytic_transactions(self, dlen=0):
        from_date = make_aware(datetime.combine(date.today() - timedelta(dlen, 0, 0), time(0,0,0)))
        to_date = make_aware(datetime.now())
        transactions = Transaction.objects.filter(
            Q(destination=self.user) | Q(source=self.user),
            txn_date_time__range=[
                from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date.strftime("%Y-%m-%d %H:%M:%S")],
        )
        return transactions

    def get_transactions_on(self, dateX):
        from_date = make_aware(datetime.combine(dateX.date(), time(0, 0, 0)))
        to_date = make_aware(datetime.combine(dateX.date(), time(23, 59, 59)))
        transactions = Transaction.objects.filter(
            Q(destination=self.user) | Q(source=self.user),
            txn_date_time__range=[
                from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date.strftime("%Y-%m-%d %H:%M:%S")],
        )
        return transactions

    def all_P2P_transactions(self, second_person):
        transactions = Transaction.objects.filter(
            (Q(destination=self.user) & Q(source=second_person)) | 
            (Q(destination=second_person) & Q(source=self.user))
        )
        return transactions

    def all_transactions(self):
        transactions = Transaction.objects.filter(
            (Q(destination=self.user)) | 
            (Q(source=self.user))
        )
        return transactions
        

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Group(models.Model):
    title = models.CharField("Group Title", max_length=64)
    members = models.ManyToManyField(Profile, related_name="group")

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
    
    def __str__(self):
        return self.title + " ( " + str(self.members.all().count()) + " )"
