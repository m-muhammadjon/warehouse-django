from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class Product(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    code = models.CharField(max_length=20, verbose_name=_("Code"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name


class RawMaterial(TimeStampedModel):
    class UnitChoices(models.TextChoices):
        M = "m", _("Meter")
        M2 = "m2", _("Square Meter")
        KG = "kg", _("Kilogram")
        PCS = "pcs", _("Piece")

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    unit = models.CharField(max_length=10, choices=UnitChoices.choices, verbose_name=_("Unit"), null=True)

    class Meta:
        verbose_name = _("Raw Material")
        verbose_name_plural = _("Raw Materials")

    def __str__(self):
        return self.name


class ProductRawMaterial(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="raw_materials")
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="products")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(
        max_length=10, choices=RawMaterial.UnitChoices.choices, verbose_name=_("Unit"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Product Raw Material")
        verbose_name_plural = _("Product Raw Materials")

    def save(self, *args, **kwargs):
        self.unit = self.raw_material.unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.raw_material.name}"


class WarehouseBatch(TimeStampedModel):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="batches")
    remainder = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Remainder"))
    unit = models.CharField(
        max_length=10, choices=RawMaterial.UnitChoices.choices, verbose_name=_("Unit"), null=True, blank=True
    )
    price = models.FloatField(verbose_name=_("Price"))

    class Meta:
        verbose_name = _("Warehouse Batch")
        verbose_name_plural = _("Warehouse Batches")

    def save(self, *args, **kwargs):
        self.unit = self.raw_material.unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.raw_material.name} - {self.remainder} {self.unit}"


class Order(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order {self.id} - {self.user}"

    def calculate_materials(self) -> None:
        """
        Calculates the required materials for each item in the order and creates corresponding OrderItemRawMaterials objects.  # noqa
        This function ensures that the available warehouse batches are appropriately utilized to fulfill the order.
        """

        # Delete existing OrderItemRawMaterials related to the current order
        OrderItemRawMaterials.objects.filter(order_item__order=self).delete()

        with transaction.atomic():
            order_item_raw_materials = []
            # Create a savepoint to rollback changes of WarehouseBatch model
            sid = transaction.savepoint()
            for item in self.items.all():
                # Iterate over each item in the order to determine required raw materials.
                for raw_material in item.product.raw_materials.all():
                    # Calculate the required quantity of the raw material
                    required_quantity = raw_material.quantity * item.quantity
                    # Iterate over each available warehouse batch to fulfill the required quantity.
                    for warehouse_batch in WarehouseBatch.objects.filter(
                        raw_material=raw_material.raw_material, remainder__gt=0
                    ).order_by("created_at"):

                        if warehouse_batch.remainder >= required_quantity:
                            # Sufficient quantity available in the warehouse batch
                            order_item_raw_materials.append(
                                OrderItemRawMaterials(
                                    order_item=item,
                                    warehouse_batch=warehouse_batch,
                                    raw_material=raw_material.raw_material,
                                    quantity=required_quantity,
                                    unit=warehouse_batch.unit,
                                    price=warehouse_batch.price,
                                )
                            )
                            warehouse_batch.remainder -= required_quantity
                            warehouse_batch.save()
                            required_quantity = 0
                            # Exit the loop to proceed to the next item.
                            break
                        else:
                            # If required quantity exceeds available stock, allocate remaining quantity from subsequent batches.  # noqa
                            # If still insufficient, create a new OrderItemRawMaterial without a warehouse batch.
                            order_item_raw_materials.append(
                                OrderItemRawMaterials(
                                    order_item=item,
                                    warehouse_batch=warehouse_batch,
                                    raw_material=raw_material.raw_material,
                                    quantity=warehouse_batch.remainder,
                                    unit=warehouse_batch.unit,
                                    price=warehouse_batch.price,
                                )
                            )
                            required_quantity -= warehouse_batch.remainder
                            warehouse_batch.remainder = 0
                            warehouse_batch.save()

                    if required_quantity > 0:
                        # Add remaining required quantity as a new OrderItemRawMaterial with no warehouse batch
                        order_item_raw_materials.append(
                            OrderItemRawMaterials(
                                order_item=item,
                                raw_material=raw_material.raw_material,
                                quantity=required_quantity,
                                unit=raw_material.unit,
                            )
                        )
            # Rollback changes of WarehouseBatch model. We should not change the state of the warehouse
            transaction.savepoint_rollback(sid)

            # Bulk create the OrderItemRawMaterials for optimized database insertion.
            OrderItemRawMaterials.objects.bulk_create(order_item_raw_materials)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class OrderItemRawMaterials(TimeStampedModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="raw_materials")
    warehouse_batch = models.ForeignKey(WarehouseBatch, on_delete=models.CASCADE, related_name="order_items", null=True)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Quantity"))
    unit = models.CharField(
        max_length=10, choices=RawMaterial.UnitChoices.choices, verbose_name=_("Unit"), null=True, blank=True
    )
    price = models.FloatField(verbose_name=_("Price"), null=True)

    class Meta:
        verbose_name = _("Order Item Raw Material")
        verbose_name_plural = _("Order Item Raw Materials")

    def __str__(self):
        return (
            f"Warehouse#{self.warehouse_batch} | {self.order_item.product.name} - {self.raw_material.name} - "
            f"{self.quantity}"
        )
