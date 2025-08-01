
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Job

@receiver(post_save, sender=User)
def reassign_jobs_if_deleted(sender, instance, **kwargs):
    if instance.is_deleted and instance.is_employer:
        try:
            default_employer = User.objects.get(username='default_employer')
            Job.objects.filter(employer=instance).update(employer=default_employer)
        except Exception as e:
            print(f"User does not exist {str(e)}")