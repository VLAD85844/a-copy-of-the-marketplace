import json
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Banner, Review
from .serializers import ProductSerializer, CategorySerializer, ProductSerializer, SaleItemSerializer, ProductFullSerializer, BannerSerializer, ReviewSerializer, BasketItemSerializer
from django.views import View
from django.core.paginator import Paginator
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
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def get(self, request):
        try:
            cart = self.get_cart(request)
            items = cart.items.all()
            serializer = BasketItemSerializer(
                items,
                many=True,
                context={'request': request}
            )
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

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

            cart = self.get_cart(request)
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
            return JsonResponse({"error": str(e)}, status=500)

    def delete(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('id')
            quantity = data.get('count', 1)

            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)

            quantity = int(quantity)
            cart = self.get_cart(request)
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
            return JsonResponse({"error": str(e)}, status=500)


class BannerListView(View):
    def get(self, request):
        banners = Banner.objects.filter(is_active=True)
        serializer = BannerSerializer(banners, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)


class SaleView(View):
    def get(self, request):
        try:
            sale_products = Product.objects.filter(sale_price__isnull=False).order_by('-date_from')

            current_page = request.GET.get('currentPage', 1)
            try:
                current_page = int(current_page)
                if current_page < 1:
                    current_page = 1
            except ValueError:
                current_page = 1

            paginator = Paginator(sale_products, 5)
            try:
                page_obj = paginator.page(current_page)
            except:
                page_obj = paginator.page(1)

            serializer = SaleItemSerializer(
                page_obj.object_list,
                many=True,
                context={'request': request}
            )

            response_data = {
                "items": serializer.data,
                "currentPage": page_obj.number,
                "lastPage": paginator.num_pages
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class CatalogView(View):
    def get(self, request):
        try:
            filters = request.GET.get('filter', {})
            name_filter = filters.get('name', '')
            min_price = float(filters.get('minPrice', 0))
            max_price = float(filters.get('maxPrice', 999999))
            free_delivery = filters.get('freeDelivery', 'false') == 'true'
            available = filters.get('available', 'false') == 'true'

            sort_field = request.GET.get('sort', 'id')
            sort_type = request.GET.get('sortType', 'inc')

            current_page = int(request.GET.get('currentPage', 1))
            limit = int(request.GET.get('limit', 20))

            products = Product.objects.all()

            if name_filter:
                products = products.filter(name__icontains=name_filter)

            products = products.filter(
                price__gte=min_price,
                price__lte=max_price
            )

            if free_delivery:
                products = products.filter(free_delivery=True)

            if available:
                products = products.filter(count__gt=0)

            if sort_type == 'dec':
                sort_field = f'-{sort_field}'
            products = products.order_by(sort_field)

            paginator = Paginator(products, limit)
            page_obj = paginator.page(current_page)

            serializer = ProductSerializer(
                page_obj.object_list,
                many=True,
                context={'request': request}
            )

            return JsonResponse({
                "items": serializer.data,
                "currentPage": page_obj.number,
                "lastPage": paginator.num_pages
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class TagsView(View):
    def get(self, request):
        try:
            tags = set()
            for product in Product.objects.all():
                if isinstance(product.tags, list):
                    tags.update(str(tag) for tag in product.tags if tag)

            formatted_tags = [
                {"id": idx, "name": tag}
                for idx, tag in enumerate(sorted(tags), 1)
            ]

            return JsonResponse(formatted_tags, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)