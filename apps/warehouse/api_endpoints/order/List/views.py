from rest_framework.generics import ListAPIView

from apps.warehouse.models import Order

from .serializers import OrderListSerializer


class OrderListAPIView(ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)


__all__ = ["OrderListAPIView"]
