from rest_framework import serializers
from .models import Product, Category, Banner, Review

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'images']

    def get_images(self, obj):
        return [{
            "src": obj.image.url if obj.image else "",
            "alt": obj.name
        }]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_featured']

class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'image', 'link']

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "alt": obj.title
        }

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author', 'email', 'text', 'rate', 'created_at']