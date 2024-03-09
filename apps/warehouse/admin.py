from django.contrib import admin

from apps.warehouse.models import Product, ProductRawMaterial, RawMaterial


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
