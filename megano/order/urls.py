from django.urls import path
from .views import OrderView, OrderDetailView, PaymentView

urlpatterns = [
    path('orders', OrderView.as_view(), name='orders'),
    path('order/<int:order_id>', OrderDetailView.as_view(), name='order-detail'),
    path('payment/<int:order_id>', PaymentView.as_view(), name='payment'),
]