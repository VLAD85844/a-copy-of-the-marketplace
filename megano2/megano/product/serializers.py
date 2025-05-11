from rest_framework import serializers
from .models import Product, Category, Banner, Review, CartItem


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.FloatField()
    title = serializers.CharField(source='name')
    freeDelivery = serializers.BooleanField(source='free_delivery')
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(
        source='categories.first.id',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date',
            'title', 'description', 'freeDelivery',
            'images', 'tags', 'reviews', 'rating'
        ]

    def get_images(self, obj):
        if obj.image:
            return [{"src": f"/media/{obj.image.url.split('/media/')[-1]}", "alt": obj.name}]
        return []

    def get_tags(self, obj):
        if isinstance(obj.tags, list):
            return [{"id": idx, "name": str(tag)} for idx, tag in enumerate(obj.tags, 1)]
        return [{"id": 1, "name": "string"}]

    def get_reviews(self, obj):
        return obj.product_reviews.count()

    def get_rating(self, obj):
        return float(obj.rating) if obj.rating else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['date'] = instance.date.strftime("%a %b %d %Y %H:%M:%S GMT+0100 (Central European Standard Time)")
        return data


class ProductFullSerializer(ProductSerializer):
    fullDescription = serializers.CharField(source='full_description')
    specifications = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField(method_name='get_full_reviews')

    class Meta(ProductSerializer.Meta):
        fields = [
            'id', 'category', 'price', 'count', 'date',
            'title', 'description', 'freeDelivery', 'fullDescription',
            'images', 'tags', 'reviews', 'specifications', 'rating'
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
        if isinstance(obj.tags, list):
            return [{"id": idx, "name": str(tag)} for idx, tag in enumerate(obj.tags, 1)]
        return [{"id": 1, "name": "string"}]


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'is_featured', 'image', 'subcategories']

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else None,
            "alt": obj.name if obj.image else "No image"
        }

    def get_subcategories(self, obj):
        return list(obj.subcategories.values_list('id', flat=True)) if obj.subcategories.exists() else []


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
            "src": obj.image.url,
            "alt": obj.title
        }


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author', 'email', 'text', 'rate', 'created_at']


class BasketItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id')
    title = serializers.CharField(source='product.name')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    category = serializers.PrimaryKeyRelatedField(source='product.categories.first', read_only=True)
    freeDelivery = serializers.BooleanField(source='product.free_delivery')
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    count = serializers.IntegerField(source='quantity')

    def get_images(self, obj):
        request = self.context.get('request')
        if obj.product.image:
            return [{"src": request.build_absolute_uri(obj.product.image.url), "alt": obj.product.name}]
        return []

    def get_tags(self, obj):
        tags = obj.product.tags
        if isinstance(tags, list):
            # Возвращаем список словарей с id и name
            return [{"id": idx, "name": str(tag)} for idx, tag in enumerate(tags, 1)]
        return []

    def get_specifications(self, obj):
        return [{"name": spec.name, "value": spec.value} for spec in obj.product.specifications.all()]

    class Meta:
        model = CartItem
        fields = [
            'id', 'title', 'price', 'count', 'category',
            'freeDelivery', 'images', 'tags', 'specifications'
        ]


class SaleItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='pk')
    salePrice = serializers.DecimalField(source='sale_price', max_digits=10, decimal_places=2)
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images']

    def get_dateFrom(self, obj):
        return obj.date_from.strftime("%m-%d") if obj.date_from else None

    def get_dateTo(self, obj):
        return obj.date_to.strftime("%m-%d") if obj.date_to else None

    def get_images(self, obj):
        if obj.image:
            return [{"src": f"/media/{obj.image.url.split('/media/')[-1]}", "alt": obj.name}]
        return []
