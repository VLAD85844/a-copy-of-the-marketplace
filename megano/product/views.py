from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.views import View


class ProductPopularView(View):
    def get(self, request):
        top_products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        product_data = ProductSerializer(top_products, many=True).data
        return JsonResponse({'items': product_data})


class ProductLimitedView(View):
    def get(self, request):
        limited_edition = Product.objects.filter(is_limited=True)
        product_data = ProductSerializer(limited_edition, many=True).data
        return JsonResponse({'items': product_data})


class CategoryListView(View):
    def get(self, request):
        featured_categories = Category.objects.filter(is_featured=True)
        category_data = CategorySerializer(featured_categories, many=True).data
        return JsonResponse({'items': category_data})


class HomeView(View):
    def get(self, request):
        featured_categories = Category.objects.filter(is_featured=True)[:3]
        top_products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        limited_edition = Product.objects.filter(is_limited=True)

        response_data = {
            'popularCards': [
                {
                    'id': product.id,
                    'title': product.name,
                    'price': float(product.price),
                    'images': [{'src': product.image.url if product.image else '', 'alt': product.name}]
                } for product in top_products
            ],
            'limitedCards': [
                {
                    'id': product.id,
                    'title': product.name,
                    'price': float(product.price),
                    'images': [{'src': product.image.url if product.image else '', 'alt': product.name}]
                } for product in limited_edition
            ],
            'featuredCategories': [
                {
                    'id': category.id,
                    'name': category.name,
                    'is_featured': category.is_featured
                } for category in featured_categories
            ]
        }

        return JsonResponse(response_data)
