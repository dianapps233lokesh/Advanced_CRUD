from django.db import transaction
from rest_framework import serializers
from .models import Milestone,Job
from django.contrib.auth import get_user_model
from portal.models import Skill

User=get_user_model()

class SkillNameField(serializers.RelatedField):
    def to_internal_value(self, data):
        # Accept skill name instead of primary key
        # print("data inside to_internal",data)
        data=data.lower().strip()
        skill_obj, _ = Skill.objects.get_or_create(skill=data)
        return skill_obj

    def to_representation(self, obj):
        return obj.skill

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['title', 'amount','is_completed_by_freelancer','is_approved_by_employer']

class JobCreateSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)
    skills = SkillNameField(many=True, queryset=Skill.objects.all())

    class Meta:
        model = Job
        fields = ['title', 'description', 'employer', 'skills','milestones']
        read_only_fields=['employer']

    @transaction.atomic
    def create(self, validated_data):
        print("validated data in job create",validated_data)
        skils=validated_data.pop("skills",None)

        validated_data['employer']=self.context.get('request').user
        milestones_data = validated_data.pop('milestones',None)

        print("milestones data",milestones_data)

        print("current user id ",self.context.get('request').user)
        job = Job.objects.create(**validated_data)
        if skils:          
            job.skills.set(skils)
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


