from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)

    def delete(self):
        self.is_deleted=True
        self.save()