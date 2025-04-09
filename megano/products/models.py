from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_featured = models.BooleanField(default=False, verbose_name="Избранная категория")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    image = models.ImageField("Изображение", upload_to='products/', blank=True, null=True)
    short_description = models.TextField("Краткое описание")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    reviews_count = models.PositiveIntegerField("Количество отзывов", default=0)
    sort_index = models.IntegerField("Индекс сортировки", default=0)
    purchase_count = models.IntegerField("Количество покупок", default=0)
    is_limited = models.BooleanField("Ограниченный тираж", default=False)
    categories = models.ManyToManyField(Category, related_name='products', verbose_name="Категории")

    class Meta:
        ordering = ['-sort_index', '-purchase_count']

    def __str__(self):
        return self.name