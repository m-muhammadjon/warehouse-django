from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderCreateSerializer


class OrderCreateAPIView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


__all__ = ["OrderCreateAPIView"]
