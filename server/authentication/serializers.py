from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'admin_subrole', 'student_id', 'department', 'is_active', 'created_at', 'display_name']
        read_only_fields = ['id', 'created_at', 'display_name']
    
    def get_display_name(self, obj):
        """Get the display name for the user"""
        return obj.get_display_name()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate_email(self, value):
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        
        # Temporarily commented out for debugging
        # # Check if email ends with wmsu.edu.ph
        # if not value.endswith('@wmsu.edu.ph'):
        #     raise serializers.ValidationError("Please use your WMSU email address")
        
        return value.lower()
    
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        return value
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError("This account has been deactivated")
            
            # Authenticate user - use email as the username field since USERNAME_FIELD = 'email'
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")
        
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data
