from django.urls import re_path, path, include
from rest_framework import routers
from rest_framework_simplejwt import views

from .views import UserViewSet

router = routers.SimpleRouter()

router.register("users", UserViewSet, basename="user")

urlpatterns = [
    re_path(r"^jwt/create/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^jwt/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^jwt/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
    path("", include(router.urls)),
]
