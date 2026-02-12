from django.db import models
from django.contrib.auth.models import User

class KhaltiPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pidx = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.IntegerField()  # in paisa
    fee = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.transaction_id} - {self.status}"
