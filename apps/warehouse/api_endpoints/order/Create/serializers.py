from rest_framework import serializers

from apps.warehouse.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "items",
        )
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def create(self, validated_data):
        order_items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        return order
