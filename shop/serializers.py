from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    num_of_products = serializers.IntegerField(source='products.count')

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'num_of_products', ]

    