from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

User=get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'is_employer', 'is_freelancer']

    def validate(self, attrs):
        if attrs.get("is_employer") and attrs.get("is_freelancer"):
            raise serializers.ValidationError("User cannot be both employer and freelancer.")
        if not attrs.get("is_employer") and not attrs.get("is_freelancer"):
            raise serializers.ValidationError("User must be either employer or freelancer")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        print("validated data in custom user serializer",validated_data)
        print("password before hashing",password)
        user = CustomUser.objects.create_user(**validated_data)
        # print("password before hashing",password)
        user.set_password(password)
        user.save()
        return user

class EmployeeSoftDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email','is_deleted']

        def update(self, instance, validated_data):
            is_deleted = validated_data.get('is_deleted', False)

            if is_deleted and not instance.is_deleted and instance.is_employer:
                instance.is_deleted = True
                instance.save()  # Signal will handle job reassignment
            return instance