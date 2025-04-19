from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Принят'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
    ]
    DELIVERY_TYPES = [
        ('ordinary', 'Обычная'),
        ('express', 'Экспресс'),
        ('free', 'Бесплатная'),
    ]
    PAYMENT_TYPES = [
        ('online', 'Онлайн'),
        ('someone', 'При получении'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPES, default='ordinary')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"