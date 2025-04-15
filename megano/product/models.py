from django.db import models
from django.contrib.auth.models import User
from django.apps import apps


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.user or self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"


class Banner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    """Модель категории товара"""
    name = models.CharField(max_length=255, verbose_name="Название категории")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_featured = models.BooleanField("Избранная категория", default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""
    name = models.CharField("Название", max_length=255)
    description = models.TextField(default="Описание отсутствует")
    full_description = models.TextField("Полное описание", default="")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    count = models.IntegerField("Количество", default=0)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    sort_index = models.IntegerField("Индекс сортировки", default=0)
    purchase_count = models.IntegerField("Количество покупок", default=0)
    short_description = models.TextField("Краткое описание", blank=True)
    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, default=4.6, null=True, blank=True)
    free_delivery = models.BooleanField("Бесплатная доставка", default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    tags = models.JSONField("Теги", default=list)
    def update_rating(self):
        reviews = self.product_reviews.filter(is_published=True)
        if reviews.exists():
            total_rates = sum(review.rate for review in reviews)
            avg_rating = total_rates / reviews.count()
            self.rating = round(avg_rating, 1)
            self.reviews = reviews.count()
            self.save()
    is_limited = models.BooleanField("Ограниченный тираж", default=False)
    categories = models.ManyToManyField(Category, related_name='products', verbose_name="Категории")

    class Meta:
        ordering = ['-sort_index', '-purchase_count']

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    author = models.CharField(max_length=100)
    email = models.EmailField()
    text = models.TextField()
    rate = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.author} for {self.product.name}"


class Specification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Size")
    value = models.CharField(max_length=100)