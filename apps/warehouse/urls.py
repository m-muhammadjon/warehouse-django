from django.urls import path

from apps.warehouse import api_endpoints

app_name = "warehouse"

urlpatterns = [
    # product urls
    path("products/list/", api_endpoints.ProductListAPIView.as_view(), name="product-list"),
    path("products/detail/<int:pk>/", api_endpoints.ProductDetailAPIView.as_view(), name="product-detail"),
    # order urls
    path("orders/create/", api_endpoints.OrderCreateAPIView.as_view(), name="order-create"),
    path("orders/list/", api_endpoints.OrderListAPIView.as_view(), name="order-list"),
    path(
        "orders/product-materials/<int:order_id>/",
        api_endpoints.OrderProductMaterialListAPIView.as_view(),
        name="order-product-materials",
    ),
    # warehouse batch urls
]
