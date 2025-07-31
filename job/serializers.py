from django.db import transaction
from rest_framework import serializers
from .models import Milestone,Job
from django.contrib.auth import get_user_model

User=get_user_model()

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['title', 'amount','is_completed_by_freelancer','is_approved_by_employer']

class JobCreateSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)

    class Meta:
        model = Job
        fields = ['title', 'description', 'employer', 'freelancer','milestones']

    @transaction.atomic
    def create(self, validated_data):
        print("validated data in job create",validated_data)

        milestones_data = validated_data.pop('milestones',None)
        freelancer = validated_data.pop('freelancer',None)

        print("milestones data",milestones_data)

        job = Job.objects.create(**validated_data)

        if freelancer:
            job.freelancer=freelancer
            job.save()

        for milestone in milestones_data:
            Milestone.objects.create(job=job, **milestone)

        return job


class EmployeeStatsSerializer(serializers.ModelSerializer):
    total_jobs=serializers.IntegerField(read_only=True,required=False)
    total_earnings=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True,required=False)
    class Meta:
        model=User
        fields=['id','username','email','total_jobs','total_earnings']

class JobStatsSerializer(serializers.ModelSerializer):
    avg_milestone=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True,required=False)
    class Meta:
        model=Job
        fields=['id','title','description','employer','freelancer','avg_milestone']