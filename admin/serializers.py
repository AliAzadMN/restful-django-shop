from django.contrib.auth.models import Group, Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', )


class GroupListRetrieveSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', )     


class GroupPermissionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = Permission
        fields = ('id', )


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    permissions = GroupPermissionSerializer(many=True, required=False)

    class Meta:
        model = Group
        fields = ('name', 'permissions', )

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])

        group = Group(**validated_data)
        group.save()

        permissions = [
            Permission.objects.get(
                id=permission['id'],
            ) for permission in permissions_data
        ]
        group.permissions.set(permissions)
        return group


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        permissions_data = validated_data.get('permissions')

        if permissions_data != None:
            permissions = [
                Permission.objects.get(
                    id=permission['id'],
                ) for permission in permissions_data
        ]
            instance.permissions.set(permissions)
        
        return instance
