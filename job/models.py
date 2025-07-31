from django.db import models

# Create your models here.


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    employer = models.ForeignKey('portal.CustomUser', on_delete=models.CASCADE, limit_choices_to={'is_employer': True}, related_name='jobs')
    freelancer = models.ForeignKey('portal.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_freelancer': True}, related_name='freelancer')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Milestone(models.Model):
    job = models.ForeignKey(Job, related_name="milestones", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed_by_freelancer = models.BooleanField(default=False)
    is_approved_by_employer = models.BooleanField(default=False)