from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)



