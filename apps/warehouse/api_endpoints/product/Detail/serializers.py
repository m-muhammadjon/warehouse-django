from rest_framework import serializers

from apps.warehouse.models import Product, ProductRawMaterial, RawMaterial


class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = ("id", "name")


class ProductRawMaterialSerializer(serializers.ModelSerializer):
    raw_material = RawMaterialSerializer()

    class Meta:
        model = ProductRawMaterial
        fields = ("raw_material", "quantity", "unit")


class ProductDetailSerializer(serializers.ModelSerializer):
    raw_materials = ProductRawMaterialSerializer(many=True)

    class Meta:
        model = Product
        fields = ("id", "name", "code", "raw_materials")
