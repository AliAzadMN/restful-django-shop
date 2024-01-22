from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from .constants import Messages
from .models import User
from .utils import decode_uid


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
    

class UserGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = Group
        fields = ("id", )
        

class UserAdminUpdateSerializer(serializers.ModelSerializer):
    groups = UserGroupSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ("groups", )
    
    def update(self, instance, validated_data):
        groups_data = validated_data.get("groups")

        instance.is_admin = bool(groups_data)
        instance.save()

        groups = [
            Group.objects.get(
                id=group['id'],
            ) for group in groups_data
        ]
        instance.groups.set(groups)

        return instance
    

class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "birth_date", "national_number", "date_joined")

    def to_representation(self, instance):
        rep =  super().to_representation(instance)

        if instance.is_admin != instance.is_superuser:
            rep['is_admin'] = True
            rep['groups'] = [
                dict(id=group.id) for group in instance.groups.all()
            ] 

        return rep   


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "birth_date", "national_number", )
    
    def update(self, instance, validated_data):
        for field in UserUpdateSerializer.Meta.fields:
            setattr(
                instance,
                field, 
                validated_data.get(field, getattr(instance, field))
            )
        instance.save()
        return instance


class CurrentPasswordSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_password": Messages.INVALID_PASSWORD_ERROR,
    }

    current_password = serializers.CharField(
        style={"input_type": "password"}, 
        write_only=True,
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        is_password_valid = user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")


class UserDeleteSerializer(CurrentPasswordSerializer):
    pass


class SetPasswordSerializer(serializers.Serializer):
    default_error_messages = {
        "password_mismatch": Messages.PASSWORD_MISMATCH_ERROR,
    }

    new_password = serializers.CharField(style={"input_type": "password"})
    re_new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        user = getattr(self, "user", None) or self.context["request"].user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None
        new_password = data["new_password"]

        try:
            validate_password(new_password, user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        re_new_password = data["re_new_password"]

        if new_password == re_new_password:
            return data
        else:
            self.fail("password_mismatch")


class UserChangePasswordSerializer(CurrentPasswordSerializer, SetPasswordSerializer):
    pass


class UserFunctionsMixin:
    def get_user(self, is_active=True):
        try:
            user = User._default_manager.get(
                is_active=is_active,
                **{self.email_field: self.data.get(self.email_field, "")},
            )
            if user.has_usable_password():
                return user
            
        except User.DoesNotExist:
            self.fail("email_not_found")


class UserResetPasswordSerializer(serializers.Serializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": Messages.EMAIL_NOT_FOUND,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_field = User.get_email_field_name()
        self.fields[self.email_field] = serializers.EmailField()
        

class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "invalid_token": Messages.INVALID_TOKEN_ERROR,
        "invalid_uid": Messages.INVALID_UID_ERROR,
    }

    def validate(self, data):
        validated_data = super().validate(data)

        try:
            uid = decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )

        is_valid_token = default_token_generator.check_token(
            self.user,
            self.initial_data.get("token", ""),
        )
        if is_valid_token:
            return validated_data
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )


class UserResetPasswordConfirmSerializer(UidAndTokenSerializer, SetPasswordSerializer):
    pass


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[f"new_{User.USERNAME_FIELD}"] = self.fields.pop(User.USERNAME_FIELD)
