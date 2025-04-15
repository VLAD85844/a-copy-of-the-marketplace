from rest_framework import serializers
from .models import Product, Category, Banner, Review


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    freeDelivery = serializers.BooleanField(source='free_delivery')
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    category = CategoryShortSerializer(source='categories.first')

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date',
            'title', 'description', 'freeDelivery',
            'images', 'tags', 'reviews', 'rating'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        if not request:
            return [{"src": "", "alt": obj.name}]
        return [{
            "src": request.build_absolute_uri(obj.image.url) if obj.image else "",
            "alt": obj.name
        }]

    def get_tags(self, obj):
        tags = obj.tags
        if isinstance(tags, list):
            if all(isinstance(tag, dict) for tag in tags):
                return [{"id": tag.get("id"), "name": tag.get("name")} for tag in tags]
            else:
                return [{"id": idx, "name": str(tag)} for idx, tag in enumerate(tags)]
        return []

    def get_reviews(self, obj):
        return obj.product_reviews.count()

    def get_rating(self, obj):
        return float(obj.rating) if obj.rating else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['date'] = instance.date.strftime("%a %b %d %Y %H:%M:%S GMT+0100 (Central European Standard Time)")
        return data


class ProductFullSerializer(ProductSerializer):
    fullDescription = serializers.CharField(source='description')
    specifications = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField(method_name='get_full_reviews')

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'fullDescription', 'specifications', 'reviews'
        ]

    def get_specifications(self, obj):
        return [{"name": spec.name, "value": spec.value} for spec in obj.specifications.all()]

    def get_full_reviews(self, obj):
        return [{
            "author": review.author,
            "email": review.email,
            "text": review.text,
            "rate": review.rate,
            "date": review.created_at.strftime("%Y-%m-%d %H:%M")
        } for review in obj.product_reviews.filter(is_published=True)]

    def get_tags(self, obj):
        tags = obj.tags
        if isinstance(tags, list):
            if all(isinstance(tag, dict) for tag in tags):
                return [{"id": tag.get("id"), "name": tag.get("name")} for tag in tags]
            else:
                return [{"id": idx, "name": tag} for idx, tag in enumerate(tags)]
        elif isinstance(tags, str):
            return [{"id": idx, "name": tag} for idx, tag in enumerate(tags.split(','))]
        return []


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
        request = self.context.get('request')
        if not request:
            return {"src": "", "alt": obj.title}
        return {
            "src": request.build_absolute_uri(obj.image.url) if obj.image else "",
            "alt": obj.title
        }


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author', 'email', 'text', 'rate', 'created_at']