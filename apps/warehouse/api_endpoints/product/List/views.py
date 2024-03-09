from rest_framework.generics import ListAPIView

from apps.warehouse.models import Product

from .serializers import ProductListSerializer


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()


__all__ = ["ProductListAPIView"]
