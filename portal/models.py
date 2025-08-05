from django.db import models
from django.contrib.auth.models import AbstractUser

class Skill(models.Model):
    skill=models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.skill

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)
    skill=models.ManyToManyField(Skill,related_name='user_skill')


    def soft_delete(self):
        self.is_deleted=True
        self.save()