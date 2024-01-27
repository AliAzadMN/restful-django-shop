from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    num_of_products = serializers.IntegerField(source='products.count')

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'num_of_products', ]


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'description', ]

    def validate(self, data):
        title = data.get('title')
        if title and len(title) < 3:
            return serializers.ValidationError("Product title length should be at least 3")
        return data
        

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title')

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'inventory', 'price', 'description', ]
        