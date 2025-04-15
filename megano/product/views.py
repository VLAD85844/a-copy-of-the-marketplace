import json
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, Banner, Review
from .serializers import ProductSerializer, CategorySerializer, ProductSerializer, ProductFullSerializer, BannerSerializer, ReviewSerializer
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ProductPopularView(View):
    def get(self, request):
        products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        serializer = ProductSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return JsonResponse(serializer.data, safe=False)


class ProductLimitedView(View):
    def get(self, request):
        limited_edition = Product.objects.filter(is_limited=True)
        serializer = ProductSerializer(
            limited_edition,
            many=True,
            context={'request': request}
        )
        return JsonResponse(serializer.data, safe=False)


class CategoryListView(View):
    def get(self, request):
        featured_categories = Category.objects.filter(is_featured=True)[:3]
        return JsonResponse(CategorySerializer(featured_categories, many=True).data, safe=False)


class ProductReviewsView(View):
    def get(self, request, product_id):
        try:
            reviews = Review.objects.filter(product_id=product_id, is_published=True)
            serializer = ReviewSerializer(reviews, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @method_decorator(csrf_exempt)
    def post(self, request, product_id):
        try:
            data = json.loads(request.body)

            required_fields = ['author', 'email', 'text', 'rate']
            if not all(key in data for key in required_fields):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            if not 1 <= data['rate'] <= 5:
                return JsonResponse({"error": "Rate must be between 1 and 5"}, status=400)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)

            Review.objects.create(
                product=product,
                author=data['author'],
                email=data['email'],
                text=data['text'],
                rate=data['rate'],
                is_published=True
            )

            product.update_rating()

            return self.get(request, product_id)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"error": "Server error"}, status=500)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductFullSerializer(product, context={'request': request})
            return JsonResponse(serializer.data)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class BasketView(View):
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({"items": []})

        try:
            cart = Cart.objects.get(session_key=session_key)
            items = cart.items.select_related('product')
            products = [item.product for item in items]

            serializer = ProductSerializer(
                products,
                many=True,
                context={'request': request}
            )
            data = serializer.data

            for i, item in enumerate(items):
                data[i]['count'] = item.quantity

            return JsonResponse({"items": data})

        except Cart.DoesNotExist:
            return JsonResponse({"items": []})

    def post(self, request):
        try:
            if request.content_type != 'application/json':
                return JsonResponse(
                    {"error": "Content-Type must be application/json"},
                    status=400
                )

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            product_id = data.get('id')
            quantity = data.get('count', 1)

            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)

            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return JsonResponse({"error": "Quantity must be positive integer"}, status=400)

            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart, created = Cart.objects.get_or_create(session_key=session_key)
            product = Product.objects.get(id=product_id)

            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()

            return self.get(request)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": "Server error"}, status=500)

    def delete(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('id')
            quantity = data.get('count', 1)

            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)

            quantity = int(quantity)
            session_key = request.session.session_key

            cart = Cart.objects.get(session_key=session_key)
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)

            if cart_item.quantity <= quantity:
                cart_item.delete()
            else:
                cart_item.quantity -= quantity
                cart_item.save()

            return self.get(request)

        except (Cart.DoesNotExist, Product.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({"error": "Not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": "Server error"}, status=500)


class BannerListView(View):
    def get(self, request):
        banners = Banner.objects.filter(is_active=True)
        serializer = BannerSerializer(banners, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
