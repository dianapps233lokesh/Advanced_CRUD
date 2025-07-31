from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'is_employer', 'is_freelancer']

    def validate(self, attrs):
        if attrs.get("is_employer") and attrs.get("is_freelancer"):
            raise serializers.ValidationError("User cannot be both employer and freelancer.")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        print("validated data in custom user serializer",validated_data)
        print("password before hashing",password)
        user = CustomUser.objects.create_user(**validated_data)
        # print("password before ha2shing",password)
        user.set_password(password)
        user.save()
        return user
