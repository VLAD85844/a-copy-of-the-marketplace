import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from product.models import Product
from .serializers import OrderSerializer


@method_decorator(csrf_exempt, name='dispatch')
class OrderView(View):
    def post(self, request):
        try:
            try:
                request_data = json.loads(request.body)
                print("Received data:", request_data)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            if isinstance(request_data, list):
                products_data = request_data
                order_data = {
                    'fullName': 'Default Name',
                    'email': 'default@example.com',
                    'phone': '70000000000',
                    'deliveryType': 'ordinary',
                    'paymentType': 'online',
                    'city': 'Default City',
                    'address': 'Default Address'
                }
            elif isinstance(request_data, dict):
                products_data = request_data.get('products', [])
                order_data = request_data
            else:
                return JsonResponse({"error": "Unsupported data format"}, status=400)

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=order_data.get('fullName', 'Default Name'),
                email=order_data.get('email', 'default@example.com'),
                phone=order_data.get('phone', '70000000000'),
                delivery_type=order_data.get('deliveryType', 'ordinary'),
                payment_type=order_data.get('paymentType', 'online'),
                total_cost=sum(
                    float(item.get('price', 0)) * int(item.get('count', 0))
                    for item in products_data
                ),
                city=order_data.get('city', 'Default City'),
                address=order_data.get('address', 'Default Address')
            )

            for item in products_data:
                try:
                    product = Product.objects.get(id=item.get('id'))
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.get('count', 1),
                        price=item.get('price', 0)
                    )
                except Product.DoesNotExist:
                    order.delete()
                    return JsonResponse(
                        {"error": f"Product with id {item.get('id')} not found"},
                        status=404
                    )

            return JsonResponse({
                "orderId": order.id,
                "status": "created",
                "detailUrl": f"/api/orders/{order.id}",
                "paymentUrl": f"/payment/{order.id}/"
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        response_data = []
        for order in orders:
            order_data = {
                "id": order.id,
                "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M"),
                "fullName": order.full_name,
                "email": order.email,
                "phone": order.phone,
                "deliveryType": order.delivery_type,
                "paymentType": order.payment_type,
                "totalCost": float(order.total_cost),
                "status": order.status,
                "city": order.city,
                "address": order.address,
                "products": []
            }

            for item in order.products.all():
                product_data = {
                    "id": item.product.id,
                    "category": item.product.categories.first().id if item.product.categories.exists() else None,
                    "price": float(item.price),
                    "count": item.quantity,
                    "title": item.product.name,
                    "description": item.product.description,
                    "freeDelivery": item.product.free_delivery,
                    "images": [
                        {
                            "src": item.product.image.url if item.product.image else "",
                            "alt": item.product.name
                        }
                    ] if item.product.image else [],
                    "tags": item.product.tags,
                    "reviews": item.product.product_reviews.count(),
                    "rating": float(item.product.rating) if item.product.rating else None
                }
                order_data["products"].append(product_data)

            response_data.append(order_data)

        return JsonResponse(response_data, safe=False)


class OrderDetailView(View):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            response_data = {
                "id": order.id,
                "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M"),
                "fullName": order.full_name,
                "email": order.email,
                "phone": order.phone,
                "deliveryType": order.delivery_type,
                "paymentType": order.payment_type,
                "totalCost": float(order.total_cost),
                "status": order.status,
                "city": order.city,
                "address": order.address,
                "products": self._get_products_data(order)
            }

            return JsonResponse(response_data)

        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            data = json.loads(request.body)

            if 'status' in data:
                if data['status'] in dict(Order.STATUS_CHOICES).keys():
                    order.status = data['status']
                    order.save()
                    return JsonResponse({
                        "status": "success",
                        "message": "Order status updated",
                        "newStatus": order.status
                    })
                return JsonResponse({"error": "Invalid status value"}, status=400)

            return JsonResponse({"error": "No valid fields provided for update"}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def _get_products_data(self, order):
        products = []
        for item in order.products.all():
            product = item.product
            products.append({
                "id": product.id,
                "category": product.categories.first().id if product.categories.exists() else None,
                "price": float(item.price),
                "count": item.quantity,
                "title": product.name,
                "description": product.description,
                "freeDelivery": product.free_delivery,
                "images": self._get_product_images(product),
                "tags": product.tags,
                "reviews": product.product_reviews.count(),
                "rating": float(product.rating) if product.rating else None
            })
        return products

    def _get_product_images(self, product):
        if not product.image:
            return []
        return [{
            "src": product.image.url,
            "alt": product.name
        }]


@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(View):
    def get(self, request, order_id):
        if not order_id or order_id == 'undefined' or not isinstance(order_id, int):
            return JsonResponse({"error": "Invalid Order ID"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            return JsonResponse({
                "orderId": order.id,
                "status": order.status,
                "totalCost": float(order.total_cost),
                "paymentUrl": f"/api/payment/{order.id}"
            })
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            data = json.loads(request.body)

            if not self._validate_payment_data(data):
                return JsonResponse({"error": "Invalid payment data"}, status=400)

            order.status = 'processing'
            order.save()

            return JsonResponse({
                "status": "payment_processing",
                "orderId": order.id,
                "message": "Payment is being processed"
            })

        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    def _validate_payment_data(self, data):
        required_fields = ['card_number', 'expiry_date', 'cvv']
        return all(field in data for field in required_fields)
