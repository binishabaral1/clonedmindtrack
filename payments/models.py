from django.db import models
from django.contrib.auth.models import User


class KhaltiPayment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pidx = models.CharField(max_length=255, unique=True)

    purchase_order_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    purchase_order_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    amount = models.IntegerField()

    total_amount = models.IntegerField(
        null=True,
        blank=True
    )

    status = models.CharField(max_length=50)

    fee = models.IntegerField(default=0)

    refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pidx
