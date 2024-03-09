from rest_framework import serializers

from apps.warehouse.models import Order


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "user",
        )
