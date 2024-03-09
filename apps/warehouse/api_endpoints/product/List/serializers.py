from rest_framework import serializers

from apps.warehouse.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "code")
