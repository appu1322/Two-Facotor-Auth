from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class newUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verify_active = models.IntegerField(default=0)
    noOfLogs = models.IntegerField(default=0)
    verification_code = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username