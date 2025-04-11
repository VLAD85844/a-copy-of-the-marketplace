from django.db import models
from django.contrib.auth.models import User


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
    description = models.TextField("Описание товара")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    count = models.IntegerField("Количество", default=0)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    sort_index = models.IntegerField("Индекс сортировки", default=0)
    purchase_count = models.IntegerField("Количество покупок", default=0)
    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, default=0)
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

