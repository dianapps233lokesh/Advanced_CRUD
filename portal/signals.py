from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from job.models import Job
from utils.logger import logging

@receiver(post_save, sender=CustomUser)
def reassign_jobs_on_soft_delete(sender, instance, **kwargs):
    if instance.is_employer and instance.is_deleted:        #if user is employer and employer is deleted then trigger
        try:
            default_employer = CustomUser.objects.get(username="default")   #there is a default user in db
        except CustomUser.DoesNotExist as e:
            return str(e)

        Job.objects.filter(employer=instance).update(employer=default_employer)
        logging.info("signal triggered and jobs are reassigned to the default user")