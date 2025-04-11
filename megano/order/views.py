from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Basket
from .serializers import OrderSerializer, BasketSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderView(APIView):
    def get(self, request):
        active_order = Order.objects.filter(
            user=request.user,
            status='active'
        ).first()
        if not active_order:
            return Response({"detail": "Активный заказ не найден"}, status=404)
        serializer = OrderSerializer(active_order)
        return Response(serializer.data)

    def post(self, request):
        basket_serializer = BasketSerializer(data=request.data)
        if not basket_serializer.is_valid():
            return Response(basket_serializer.errors, status=400)

        try:
            basket = Basket.objects.get(id=basket_serializer.validated_data['id'])
            new_order = Order.objects.create(
                user=request.user,
                basket=basket,
                order_id=f"ORDER-{basket.id}-{request.user.id}"
            )
            return Response({"orderId": new_order.id}, status=201)
        except Basket.DoesNotExist:
            return Response({"detail": "Корзина не найдена"}, status=404)
