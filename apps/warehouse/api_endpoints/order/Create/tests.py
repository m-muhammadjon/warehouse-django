from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.warehouse.models import Product


class OrderCreateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.product_1 = Product.objects.create(
            name="Product1",
            code="ProductCode1",
        )
        self.product_2 = Product.objects.create(
            name="Product2",
            code="ProductCode2",
        )
        self.url = reverse("warehouse:order-create")

    def test_create_order_with_valid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "items": [
                {
                    "product": self.product_1.id,
                    "quantity": 10,
                },
                {
                    "product": self.product_2.id,
                    "quantity": 20,
                },
            ],
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"], self.user.id)
        self.assertEqual(response.json()["items"][0]["product"], self.product_1.id)
        self.assertEqual(response.json()["items"][0]["quantity"], 10)
        self.assertEqual(response.json()["items"][1]["product"], self.product_2.id)
        self.assertEqual(response.json()["items"][1]["quantity"], 20)

    def test_create_order_with_invalid_product_id(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "items": [
                {
                    "product": 100,
                    "quantity": 10,
                },
            ],
        }

        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"items": [{"product": ['Invalid pk "100" - object does not exist.']}]})

    def test_create_order_without_authentication(self):
        data = {
            "items": [
                {
                    "product": self.product_1.id,
                    "quantity": 10,
                },
            ],
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {"detail": "Authentication credentials were not provided."})
