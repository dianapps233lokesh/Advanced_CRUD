# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from job.models import Job

@receiver(post_save, sender=CustomUser)
def reassign_jobs_on_soft_delete(sender, instance, **kwargs):
    if instance.is_employer and instance.is_deleted:
        try:
            default_employer = CustomUser.objects.get(username="default")
        except CustomUser.DoesNotExist:
            return  # Optionally raise an error or log this

        Job.objects.filter(employer=instance).update(employer=default_employer)
