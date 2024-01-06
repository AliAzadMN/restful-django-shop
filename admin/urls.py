from rest_framework import routers

from .views import GroupViewSet

router = routers.SimpleRouter()

router.register("groups", GroupViewSet, basename="group")

urlpatterns = router.urls 
