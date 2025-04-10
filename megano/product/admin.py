from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'sort_index', 'purchase_count', 'is_limited']
    list_filter = ['price', 'is_limited']
    search_fields = ['name', 'short_description']
    filter_horizontal = ['categories']
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'short_description', 'price')
        }),
        ({
            'fields': ('sort_index', 'purchase_count', 'is_limited', 'categories'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured']
    list_editable = ['is_featured']
    search_fields = ['name']
