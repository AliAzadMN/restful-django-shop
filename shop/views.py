from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category
from .permissions import IsInGroup
from .serializers import CategorySerializer, CategoryCreateUpdateSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.prefetch_related("products")
    required_group = "Product Management"
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInGroup(), ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer
    
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.products.count() > 0:
            return Response(
                data={"Error": "There is some products relating this category. Please remove them first"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
