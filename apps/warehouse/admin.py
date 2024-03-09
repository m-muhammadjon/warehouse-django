from django.contrib import admin

from apps.warehouse.models import (Product, ProductRawMaterial, RawMaterial,
                                   WarehouseBatch)


class ProductRawMaterialInline(admin.TabularInline):
    model = ProductRawMaterial
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "code"]
    list_display_links = ["id", "name"]
    search_fields = ["name", "code"]
    inlines = [ProductRawMaterialInline]


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]


@admin.register(WarehouseBatch)
class WarehouseBatchAdmin(admin.ModelAdmin):
    list_display = ["id", "raw_material", "remainder", "price"]
    list_display_links = ["id", "raw_material"]
    search_fields = ["raw_material__name"]
