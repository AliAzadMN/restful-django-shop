from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.settings import api_settings

from .constants import Messages
from .models import User

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', )     


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'is_admin', 'date_joined', 'groups', )
    

class UserCreateSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "password_mismatch": Messages.PASSWORD_MISMATCH_ERROR,
        "cannot_create_user": Messages.CANNOT_CREATE_USER_ERROR,
    }

    password = serializers.CharField(
        style={"input_type": "password"}, 
        write_only=True,
    )

    re_password = serializers.CharField(
        style={"input_type": "password"}, 
        write_only=True,
    )

    class Meta:
        model = User
        fields = ('email', 'password', 're_password', )

    def validate(self, data):
        re_password = data.pop("re_password")

        user = User(**data)
        password = data.get("password")

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )
        
        if data["password"] == re_password:
            return data
        else:
            self.fail("password_mismatch")

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user
