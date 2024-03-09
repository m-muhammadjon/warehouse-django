from django.urls import reverse
from rest_framework.test import APITestCase

from apps.warehouse.models import Product, ProductRawMaterial, RawMaterial


class ProductDetailAPITest(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Product",
            code="ProductCode",
        )
        self.raw_material_1 = RawMaterial.objects.create(name="RawMaterial1", unit="m")
        self.raw_material_2 = RawMaterial.objects.create(name="RawMaterial2", unit="pcs")
        ProductRawMaterial.objects.create(product=self.product, raw_material=self.raw_material_1, quantity=4)
        ProductRawMaterial.objects.create(product=self.product, raw_material=self.raw_material_2, quantity=2)

        self.url = lambda product_id: reverse("warehouse:product-detail", kwargs={"pk": product_id})

    def test_get_product_detail(self):
        response = self.client.get(self.url(self.product.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.product.id)
        self.assertEqual(response.json()["name"], self.product.name)
        self.assertEqual(response.json()["code"], self.product.code)
        self.assertEqual(len(response.json()["raw_materials"]), 2)
        self.assertEqual(response.json()["raw_materials"][0]["raw_material"]["name"], self.raw_material_1.name)
        self.assertEqual(response.json()["raw_materials"][0]["quantity"], "4.00")
        self.assertEqual(response.json()["raw_materials"][0]["unit"], "m")

    def test_get_invalid_product_detail(self):
        response = self.client.get(self.url(100))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {"detail": "Not found."})
