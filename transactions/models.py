from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):

    txn_type_choices = (
        (0, "Debit"),
        (1, "Credit")
    )

    amount = models.FloatField("Amount")
    txn_id = models.CharField("Transaction ID", max_length=20, unique=True)
    description = models.CharField("Description", max_length=145)
    source = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="source")
    active = models.BooleanField("Unsettled", default=True)
    destination = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="destination",
        null=True,
        blank=True)
    txn_type = models.IntegerField(choices=txn_type_choices)
    status = models.CharField("Status", max_length=10)
    currency = models.CharField("Currency", default="INR", max_length=5)
    txn_date_time = models.DateTimeField("DateTime", auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return  self.description + " " + self.currency + " " + str(self.amount)

    def settle(self):
        if self.active:
            return False
        else:
            self.active = False
            return True
