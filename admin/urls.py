from django.urls import path
from rest_framework import routers

from .views import GroupViewSet, PermissionListView

router = routers.SimpleRouter()

router.register("groups", GroupViewSet, basename="group")

urlpatterns = [
    path("permissions/", PermissionListView.as_view(), name="permission-list")
] + router.urls
