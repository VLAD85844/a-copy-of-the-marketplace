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
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)  # ← Указываем как строку
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        Product = apps.get_model('product', 'Product')
        return self.quantity * Product.objects.get(id=self.product_id).price

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
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    count = models.IntegerField("Количество", default=0)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    sort_index = models.IntegerField("Индекс сортировки", default=0)
    purchase_count = models.IntegerField("Количество покупок", default=0)
    short_description = models.TextField("Краткое описание", blank=True)
    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, null=True, blank=True)
    free_delivery = models.BooleanField("Бесплатная доставка", default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    tags = models.JSONField("Теги", default=list)
    reviews = models.PositiveIntegerField("Количество отзывов", default=0)
    is_limited = models.BooleanField("Ограниченный тираж", default=False)
    categories = models.ManyToManyField(Category, related_name='products', verbose_name="Категории")

    class Meta:
        ordering = ['-sort_index', '-purchase_count']

    def __str__(self):
        return self.name

