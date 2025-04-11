import json
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, Banner, Review
from .serializers import ProductSerializer, CategorySerializer
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ProductPopularView(View):
    def get(self, request):
        products = Product.objects.order_by('-sort_index', '-purchase_count')[:8]
        return JsonResponse(ProductSerializer(products, many=True).data, safe=False)


class ProductLimitedView(View):
    def get(self, request):
        limited_edition = Product.objects.filter(is_limited=True)
        return JsonResponse(ProductSerializer(limited_edition, many=True).data, safe=False)


class CategoryListView(View):
    def get(self, request):
        featured_categories = Category.objects.filter(is_featured=True)[:3]
        return JsonResponse(CategorySerializer(featured_categories, many=True).data, safe=False)


class ProductReviewsView(View):
    def get(self, request, product_id):
        try:
            reviews = Review.objects.filter(product_id=product_id, is_published=True)
            serialized_reviews = []
            for review in reviews:
                serialized_reviews.append({
                    "author": review.author,
                    "email": review.email,
                    "text": review.text,
                    "rate": review.rate,
                    "createdAt": review.created_at.strftime("%Y-%m-%d")
                })
            return JsonResponse(serialized_reviews, safe=False)
        except Exception as e:
            print(f"Error getting reviews: {str(e)}")
            return JsonResponse({"error": "Server error"}, status=500)

    @method_decorator(csrf_exempt)
    def post(self, request, product_id):
        try:
            data = json.loads(request.body)

            if not all(key in data for key in ['author', 'email', 'text', 'rate']):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            if not 1 <= data['rate'] <= 5:
                return JsonResponse({"error": "Rate must be between 1 and 5"}, status=400)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)

            review = Review.objects.create(
                product=product,
                author=data['author'],
                email=data['email'],
                text=data['text'],
                rate=data['rate']
            )

            product.update_rating()

            return JsonResponse({
                "success": True,
                "id": review.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return JsonResponse({"error": "Server error"}, status=500)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            reviews = product.product_reviews.filter(is_published=True).order_by('-created_at')[:5]

            product_data = ProductSerializer(product).data

            product_data["reviews"] = [{
                "author": review.author,
                "email": review.email,
                "text": review.text,
                "rate": review.rate,
                "createdAt": review.created_at.strftime("%Y-%m-%d")
            } for review in reviews]

            print(f"Returning product data for ID {product_id}: {product_data}")
            return JsonResponse(product_data)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
        except Exception as e:
            print(f"Error in product detail view: {str(e)}")
            return JsonResponse({"error": "Server error"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BasketView(View):
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({"items": []})

        try:
            cart = Cart.objects.get(session_key=session_key)
            items = cart.items.select_related('product')

            data = {
                "items": [{
                    "id": item.id,
                    "productId": item.product.id,
                    "title": item.product.name,
                    "price": float(item.product.price),
                    "count": item.quantity,
                    "images": [{
                        "src": item.product.image.url if item.product.image else "",
                        "alt": item.product.name
                    }]
                } for item in items]
            }
            return JsonResponse(data)

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
                print("Received data:", data)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            product_id = data.get('id') or data.get('product_id')
            quantity = data.get('count') or data.get('quantity', 1)

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
                request.session.modified = True
                print("New session created:", session_key)

            cart, created = Cart.objects.get_or_create(session_key=session_key)
            if created:
                print("New cart created for session:", session_key)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)

            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()

            print(f"Cart item {'created' if item_created else 'updated'}: {cart_item.id}")

            response_data = {
                "success": True,
                "id": cart_item.id,
                "productId": product.id,
                "count": cart_item.quantity,
                "totalItems": cart.items.count()
            }

            return JsonResponse(response_data, status=201)

        except Exception as e:
            print("Error in basket post:", str(e))
            return JsonResponse({"error": "Server error"}, status=500)

    def _create_session(self, request):
        request.session.create()
        request.session.modified = True
        return request.session.session_key


class BannerListView(View):
    def get(self, request):
        banners = Banner.objects.filter(is_active=True)
        data = [
            {
                "id": banner.id,
                "title": banner.title,
                "description": banner.description,
                "image": {
                    "src": banner.image.url if banner.image else "",
                    "alt": banner.title
                },
                "link": banner.link
            }
            for banner in banners
        ]
        return JsonResponse(data, safe=False)