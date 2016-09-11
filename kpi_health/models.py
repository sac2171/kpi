from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FitbitCredentials(models.Model):
    user = models.OneToOneField(User)
    fitbit_user_id = models.TextField()
    access_token  = models.TextField()
    refresh_token = models.TextField()
    scopes = models.TextField()
