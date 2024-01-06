from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .permissions import IsSuperUser
from .serializers import GroupListRetrieveSerializer, GroupCreateUpdateSerializer


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.prefetch_related('permissions').order_by('id')
    permission_classes = (IsSuperUser, )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GroupListRetrieveSerializer
        return GroupCreateUpdateSerializer
    
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if group.user_set.count() > 0:
            return Response(
                data=f"The {group.name} group includes some admin users! Please remove them first.",
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
