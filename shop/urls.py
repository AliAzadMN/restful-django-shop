from rest_framework import routers

from .views import CategoryViewSet, ProductViewSet

router = routers.DefaultRouter()

router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")

urlpatterns = router.urls
