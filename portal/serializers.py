from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Skill
from django.db import transaction
from utils.logger import logging

User=get_user_model()

class SkillNameField(serializers.RelatedField):
    def to_internal_value(self, data):
        # Accept skill name instead of primary key
        # print("data inside to_internal",data)
        data=data.lower().strip()
        logging.info(f"skill after the transformation:{data}")
        skill_obj, _ = Skill.objects.get_or_create(skill=data)
        return skill_obj

    def to_representation(self, obj):
        return obj.skill

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    skill = SkillNameField(many=True, queryset=Skill.objects.all(),required=False) 
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'is_employer', 'is_freelancer','skill']

    def validate(self, attrs):
        if attrs.get("is_employer") and attrs.get("is_freelancer"):
            raise serializers.ValidationError("User cannot be both employer and freelancer.")
        if not attrs.get("is_employer") and not attrs.get("is_freelancer"):
            raise serializers.ValidationError("User must be either employer or freelancer")
        return attrs
    

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password",None)
        skills = validated_data.pop("skill",None)
        logging.info(f"validated data in custom user serializer {validated_data}")
        user = User.objects.create_user(**validated_data)

        user.set_password(password)
        if skills and validated_data['is_freelancer']:
            user.skill.set(skills)
            logging.info("skills set successfully for user")
        user.save()
        return user
       
class AddSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model=Skill
        fields="__all__"

    def create(self,validated_data):
        logging.info(f"validated data {validated_data}")
        validated_data['skill']=validated_data['skill'].lower().strip()   #convert to lower case and remove extra spaces (not between)
        logging.info(f"validated data after lower {validated_data}")
        skill=Skill.objects.create(**validated_data)
        return skill