from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from product.serializers import ProductSerializer

class OrderItemProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date',
            'title', 'description', 'freeDelivery',
            'images', 'tags', 'reviews', 'rating'
        ]

    def get_category(self, obj):
        return obj.categories.first().id if obj.categories.exists() else None

    def get_images(self, obj):
        return [{
            "src": obj.image.url if obj.image else None,
            "alt": obj.name
        }] if obj.image else []

    def get_tags(self, obj):
        return [{"id": idx, "name": tag} for idx, tag in enumerate(obj.tags, 1)]

    def get_reviews(self, obj):
        return obj.product_reviews.count()

    def get_rating(self, obj):
        return float(obj.rating) if obj.rating else None

class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    count = serializers.IntegerField(source='quantity')
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product', 'count', 'price']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(source='products', many=True)
    createdAt = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M")
    deliveryType = serializers.CharField(source='delivery_type')
    paymentType = serializers.CharField(source='payment_type')
    totalCost = serializers.DecimalField(source='total_cost', max_digits=10, decimal_places=2)
    fullName = serializers.CharField(source='full_name')

    class Meta:
        model = Order
        fields = [
            'id', 'createdAt', 'fullName', 'email', 'phone',
            'deliveryType', 'paymentType', 'totalCost', 'status',
            'city', 'address', 'products'
        ]
