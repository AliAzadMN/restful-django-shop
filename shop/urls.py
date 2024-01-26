from rest_framework import routers

from .views import CategoryViewSet

router = routers.DefaultRouter()

router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
