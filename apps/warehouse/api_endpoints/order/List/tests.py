from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.warehouse.models import Order, OrderItem, Product


class OrderCreateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.user_2 = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
        )

        self.product_1 = Product.objects.create(
            name="Product1",
            code="ProductCode1",
        )
        self.product_2 = Product.objects.create(
            name="Product2",
            code="ProductCode2",
        )

        self.order_1 = Order.objects.create(
            user=self.user,
        )
        for product in [self.product_1, self.product_2]:
            OrderItem.objects.create(
                order=self.order_1,
                product=product,
                quantity=10,
            )
        self.order_2 = Order.objects.create(
            user=self.user_2,
        )
        for product in [self.product_1, self.product_2]:
            OrderItem.objects.create(
                order=self.order_2,
                product=product,
                quantity=10,
            )

        self.url = reverse("warehouse:order-list")

    def test_get_order_list_without_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_get_order_list_with_auth(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["user"], self.user.id)
