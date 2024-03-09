from django.urls import reverse
from rest_framework.test import APITestCase

from apps.warehouse.models import Product


class ProductListAPITest(APITestCase):
    def setUp(self):
        self.product_1 = Product.objects.create(
            name="Product1",
            code="ProductCode1",
        )
        self.product_2 = Product.objects.create(
            name="Product2",
            code="ProductCode2",
        )

        self.url = reverse("warehouse:product-list")

    def test_get_product_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["name"], self.product_1.name)
        self.assertEqual(response.json()["results"][1]["name"], self.product_2.name)
