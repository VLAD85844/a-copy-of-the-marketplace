from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProductSerializer, CategorySerializer
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import Product, Category


class ProductPopularAPIView(APIView):
    def post(self, request):
        data = request.data
        filtered_products = Product.objects.filter(category=data['category'])
        products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        serializer = ProductSerializer(products, many=True)
        return Response({'items': serializer.data})


class ProductLimitedAPIView(APIView):
    def post(self, request):
        data = request.data
        products = Product.objects.filter(is_limited=True)
        serializer = ProductSerializer(products, many=True)

        return Response({'items': serializer.data})



class CategoryListAPIView(APIView):
    def post(self, request):
        data = request.data
        categories = Category.objects.filter(is_featured=True)
        serializer = CategorySerializer(categories, many=True)
        return Response({'items': serializer.data})


class BannerListAPIView(APIView):
    def post(self, request):
        data = request.data
        return Response({
            'items': []
        })


class BasketAPIView(APIView):
    def post(self, request):
        data = request.data
        return Response({
            'items': []
        })


class HomeView(View):
    def post(self, request):
        data = request.data
        banners = []

        featured_categories = Category.objects.filter(is_featured=True)[:3]
        top_products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        limited_edition = Product.objects.filter(is_limited=True)

        response_data = {
            'banners': banners,
            'popularCards': [
                {
                    'id': product.id,
                    'title': product.name,
                    'price': float(product.price),
                    'images': [{
                        'src': product.image.url if product.image else '',
                        'alt': product.name
                    }]
                } for product in top_products
            ],
            'limitedCards': [
                {
                    'id': product.id,
                    'title': product.name,
                    'price': float(product.price),
                    'images': [{
                        'src': product.image.url if product.image else '',
                        'alt': product.name
                    }]
                } for product in limited_edition
            ]
        }

        return JsonResponse(response_data)


@api_view(['GET'])
def home_api(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)


class CatalogView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'catalog.html', {'products': products})


class ProductDetailView(View):
    def get(self, request, id):
        product = Product.objects.get(id=id)
        return render(request, 'product_detail.html', {'product': product})
