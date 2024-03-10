from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.warehouse.models import (Order, OrderItem, Product,
                                   ProductRawMaterial, RawMaterial,
                                   WarehouseBatch)


class OrderProductMaterialsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        # Create raw materials
        self.raw_material_1 = RawMaterial.objects.create(
            name="RawMaterial1",
            unit="m",
        )
        self.raw_material_2 = RawMaterial.objects.create(
            name="RawMaterial2",
            unit="kg",
        )
        self.raw_material_3 = RawMaterial.objects.create(
            name="RawMaterial3",
            unit="pcs",
        )
        # Create products
        self.product_1 = Product.objects.create(
            name="Product1",
            code="ProductCode1",
        )
        self.product_2 = Product.objects.create(
            name="Product2",
            code="ProductCode2",
        )
        # Add raw materials to product 1
        ProductRawMaterial.objects.create(
            product=self.product_1,
            raw_material=self.raw_material_1,
            quantity=5,
        )
        ProductRawMaterial.objects.create(
            product=self.product_1,
            raw_material=self.raw_material_2,
            quantity=10,
        )
        ProductRawMaterial.objects.create(
            product=self.product_1,
            raw_material=self.raw_material_3,
            quantity=3,
        )
        # Add raw materials to product 2
        ProductRawMaterial.objects.create(
            product=self.product_2,
            raw_material=self.raw_material_2,
            quantity=7,
        )
        ProductRawMaterial.objects.create(
            product=self.product_2,
            raw_material=self.raw_material_3,
            quantity=2,
        )
        # Create warehouse batches
        # Warehouse id | Material | Remainder | Price
        # 1            | 1        | 30        | 1200
        # 2            | 1        | 100       | 1400
        # 3            | 2        | 20        | 1700
        # 4            | 2        | 40        | 2500
        # 5            | 3        | 25        | 3200
        self.warehouse_batch_1 = WarehouseBatch.objects.create(
            raw_material=self.raw_material_1,
            remainder=30,
            price=1200,
        )
        self.warehouse_batch_2 = WarehouseBatch.objects.create(
            raw_material=self.raw_material_1,
            remainder=100,
            price=1400,
        )
        self.warehouse_batch_3 = WarehouseBatch.objects.create(
            raw_material=self.raw_material_2,
            remainder=20,
            price=1700,
        )
        self.warehouse_batch_4 = WarehouseBatch.objects.create(
            raw_material=self.raw_material_2,
            remainder=40,
            price=2500,
        )
        self.warehouse_batch_5 = WarehouseBatch.objects.create(
            raw_material=self.raw_material_3,
            remainder=25,
            price=3200,
        )

        self.url = lambda order_id: reverse("warehouse:order-product-materials", kwargs={"order_id": order_id})
        self.client.force_authenticate(user=self.user)

    def test_get_order_product_materials_case_1(self):
        """
        In this case,
        for product 1 we need:
            25 raw_material_1
            50 raw_material_2
            15 raw_material_3
        for product 2 we need:
            70 raw_material_2
            20 raw_material_3
        """
        order = Order.objects.create(
            user=self.user,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product_1,
            quantity=5,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product_2,
            quantity=10,
        )
        order.calculate_materials()

        response = self.client.get(self.url(order.id))

        self.assertEqual(response.status_code, 200)
        # Check raw materials for product 1
        self.assertEqual(response.json()["results"][0]["product"], self.product_1.name)
        self.assertEqual(response.json()["results"][0]["quantity"], 5)
        self.assertEqual(
            response.json()["results"][0]["product_materials"][0]["material_name"], self.raw_material_1.name
        )
        self.assertEqual(response.json()["results"][0]["product_materials"][0]["quantity"], 25.0)
        self.assertEqual(response.json()["results"][0]["product_materials"][0]["warehouse_batch"], 1)
        self.assertEqual(response.json()["results"][0]["product_materials"][0]["price"], 1200.0)
        self.assertEqual(
            response.json()["results"][0]["product_materials"][1]["material_name"], self.raw_material_2.name
        )
        self.assertEqual(response.json()["results"][0]["product_materials"][1]["quantity"], 20.0)
        self.assertEqual(response.json()["results"][0]["product_materials"][1]["warehouse_batch"], 3)
        self.assertEqual(response.json()["results"][0]["product_materials"][1]["price"], 1700.0)
        self.assertEqual(
            response.json()["results"][0]["product_materials"][2]["material_name"], self.raw_material_2.name
        )
        self.assertEqual(response.json()["results"][0]["product_materials"][2]["quantity"], 30.0)
        self.assertEqual(response.json()["results"][0]["product_materials"][2]["warehouse_batch"], 4)
        self.assertEqual(response.json()["results"][0]["product_materials"][2]["price"], 2500.0)
        self.assertEqual(
            response.json()["results"][0]["product_materials"][3]["material_name"], self.raw_material_3.name
        )
        self.assertEqual(response.json()["results"][0]["product_materials"][3]["quantity"], 15.0)
        self.assertEqual(response.json()["results"][0]["product_materials"][3]["warehouse_batch"], 5)
        self.assertEqual(response.json()["results"][0]["product_materials"][3]["price"], 3200.0)
        # Check raw materials for product 2
        self.assertEqual(response.json()["results"][1]["product"], self.product_2.name)
        self.assertEqual(response.json()["results"][1]["quantity"], 10)
        self.assertEqual(
            response.json()["results"][1]["product_materials"][0]["material_name"], self.raw_material_2.name
        )
        self.assertEqual(response.json()["results"][1]["product_materials"][0]["quantity"], 10.0)
        self.assertEqual(response.json()["results"][1]["product_materials"][0]["warehouse_batch"], 4)
        self.assertEqual(response.json()["results"][1]["product_materials"][0]["price"], 2500.0)
        self.assertEqual(
            response.json()["results"][1]["product_materials"][1]["material_name"], self.raw_material_2.name
        )
        self.assertEqual(response.json()["results"][1]["product_materials"][1]["quantity"], 60.0)
        self.assertEqual(response.json()["results"][1]["product_materials"][1]["warehouse_batch"], None)
        self.assertEqual(response.json()["results"][1]["product_materials"][1]["price"], None)
        self.assertEqual(
            response.json()["results"][1]["product_materials"][2]["material_name"], self.raw_material_3.name
        )
        self.assertEqual(response.json()["results"][1]["product_materials"][2]["quantity"], 10.0)
        self.assertEqual(response.json()["results"][1]["product_materials"][2]["warehouse_batch"], 5)
        self.assertEqual(response.json()["results"][1]["product_materials"][2]["price"], 3200.0)
        self.assertEqual(
            response.json()["results"][1]["product_materials"][3]["material_name"], self.raw_material_3.name
        )
        self.assertEqual(response.json()["results"][1]["product_materials"][3]["quantity"], 10.0)
        self.assertEqual(response.json()["results"][1]["product_materials"][3]["warehouse_batch"], None)
        self.assertEqual(response.json()["results"][1]["product_materials"][3]["price"], None)
        # Check warehouse batch remainders are not changed
        self.warehouse_batch_1.refresh_from_db()
        self.warehouse_batch_2.refresh_from_db()
        self.warehouse_batch_3.refresh_from_db()
        self.warehouse_batch_4.refresh_from_db()
        self.warehouse_batch_5.refresh_from_db()
        self.assertEqual(self.warehouse_batch_1.remainder, 30)
        self.assertEqual(self.warehouse_batch_2.remainder, 100)
        self.assertEqual(self.warehouse_batch_3.remainder, 20)
        self.assertEqual(self.warehouse_batch_4.remainder, 40)
        self.assertEqual(self.warehouse_batch_5.remainder, 25)
