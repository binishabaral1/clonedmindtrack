#from django.contrib.auth.models import AbstractUser
#from django.db import models

#class CustomUser(AbstractUser):
    # We'll add custom fields later
#    free_analyses_used = models.IntegerField(default=0)
#    is_premium = models.BooleanField(default=False)
    
#    def can_analyze_free(self):
#        return self.free_analyses_used < 3
    
#    def __str__(self):
#        return self.email
# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def upgrade_to_premium(self, days=30):
        """Upgrade user to premium for X days."""
        self.is_premium = True
        self.premium_until = timezone.now() + timedelta(days=days)
        self.save()


# Signal to create Profile automatically whenever a new User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
