from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.logger import logging
from django.contrib.auth.base_user import BaseUserManager

class Skill(models.Model):
    skill=models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.skill

class OnlyActive(BaseUserManager):
    def get_queryset(self):
        logging.info("OnlyActive custom manager has been called.")
        return super().get_queryset().filter(is_active=True)

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)
    skill=models.ManyToManyField(Skill,related_name='user_skill')
    objects=BaseUserManager()       #Default manager for custom user
    only_active=OnlyActive()


    def soft_delete(self):
        self.is_deleted=True
        self.save()

    class Meta:
        default_manager_name='objects'