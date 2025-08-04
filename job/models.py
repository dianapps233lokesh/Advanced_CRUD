from django.db import models
from rest_framework.exceptions import ValidationError
# Create your models here.


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills=models.ManyToManyField('portal.Skill',related_name='skill_job')
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

    # def save(self,*args,**kwargs):
    #     if self.is_completed_by_freelancer:
    #         if not self.job.freelancer:
    #             raise ValidationError("can't mark milestone complete if not assigned to freelancer")
            
    #     if self.is_approved_by_employer:
    #         if not self.is_completed_by_freelancer:
    #             raise ValidationError("employer can't approve milestone if not completed")

    def __str__(self):
        return self.title