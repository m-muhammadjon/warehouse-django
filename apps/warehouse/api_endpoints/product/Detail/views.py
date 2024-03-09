from rest_framework.generics import RetrieveAPIView

from apps.warehouse.models import Product

from .serializers import ProductDetailSerializer


class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


__all__ = ["ProductDetailAPIView"]
