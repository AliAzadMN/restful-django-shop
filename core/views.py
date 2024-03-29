from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .email import PasswordResetEmail
from .models import User
from .permissions import IsSuperUser, IsNotAuthenticated
from .serializers import (
     UserChangePasswordSerializer,
     UserChangeUsernameSerializer,
     UserDeleteSerializer,
     UserResetPasswordConfirmSerializer,
     UserResetPasswordSerializer,
     UserRetrieveSerializer,
     UserSerializer,
     UserCreateSerializer,
     UserAdminUpdateSerializer,
     UserUpdateSerializer,
)


class UserViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = User.objects.prefetch_related("groups")
        if self.action == 'list':
            return queryset
        return queryset.exclude(is_superuser=True)
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsNotAuthenticated(), ]
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsSuperUser(), ]
        if self.action in ['me', 'change_password', 'change_username']:
            return [IsAuthenticated(), ]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserAdminUpdateSerializer
        if self.action == 'me':
            if self.request.method == 'GET':
                return UserRetrieveSerializer
            if self.request.method in ['PUT', 'PATCH']:
                return UserUpdateSerializer
            if self.request.method == 'DELETE':
                return UserDeleteSerializer
        if self.action == 'change_password':
            return UserChangePasswordSerializer
        if self.action == 'reset_password':
            return UserResetPasswordSerializer
        if self.action == 'reset_password_confirm':
            return UserResetPasswordConfirmSerializer
        if self.action == 'change_username':
            return UserChangeUsernameSerializer
        return UserSerializer
    
    def create_update_resource(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        return self.create_update_resource(request)
        
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        return self.create_update_resource(request, instance=user)

    @action(detail=False, methods=['GET', 'PUT', 'PATCH', 'DELETE'])
    def me(self, request, *args, **kwargs):
        user = User.objects.prefetch_related("groups").get(id=request.user.id)

        if request.method == 'GET':
            serializer = self.get_serializer(instance=user)
            return Response(serializer.data)
        
        if request.method in ['PUT', 'PATCH']:
            return self.create_update_resource(request, instance=user)
        
        if request.method == 'DELETE':
            serializer = self.get_serializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])    
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data['new_password']
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['POST'])
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            email = PasswordResetEmail(request, context)
            email.send(to=[user.email])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data['new_password']
        serializer.user.set_password(new_password)
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'], url_path=f"change_{User.USERNAME_FIELD}")
    def change_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        new_username = serializer.data["new_" + User.USERNAME_FIELD]
        setattr(user, User.USERNAME_FIELD, new_username)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
