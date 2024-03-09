from rest_framework import serializers

from apps.warehouse.models import OrderItem, OrderItemRawMaterials


class OrderItemRawMaterialsSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="raw_material.name")

    class Meta:
        model = OrderItemRawMaterials
        fields = ("material_name", "warehouse_batch", "quantity", "unit", "price")


class OrderProductMaterialSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")
    product_materials = OrderItemRawMaterialsSerializer(many=True, source="raw_materials")

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "product_materials")
