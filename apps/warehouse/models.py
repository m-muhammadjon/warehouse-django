from django.db import models
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
    name = models.CharField(max_length=255, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Raw Material")
        verbose_name_plural = _("Raw Materials")

    def __str__(self):
        return self.name


class ProductRawMaterial(TimeStampedModel):
    class UnitChoices(models.TextChoices):
        M = "m", _("Meter")
        M2 = "m2", _("Square Meter")
        KG = "kg", _("Kilogram")
        PCS = "pcs", _("Piece")

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="raw_materials")
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="products")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UnitChoices.choices, verbose_name=_("Unit"))

    class Meta:
        verbose_name = _("Product Raw Material")
        verbose_name_plural = _("Product Raw Materials")

    def __str__(self):
        return f"{self.product.name} - {self.raw_material.name}"