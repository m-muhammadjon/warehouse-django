from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.warehouse.models import OrderItem

from .serializers import OrderProductMaterialSerializer


class OrderProductMaterialListAPIView(ListAPIView):
    serializer_class = OrderProductMaterialSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderItem.objects.filter(order_id=self.kwargs["order_id"], order__user=self.request.user)


__all__ = ["OrderProductMaterialListAPIView"]
