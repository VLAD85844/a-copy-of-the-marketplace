from django.urls import path
from .views import ProductPopularView, ProductLimitedView, SaleView, BasketView, CatalogView, TagsView, BannerListView, CategoryListView, ProductDetailView, ProductReviewsView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('popular', ProductPopularView.as_view(), name='api-popular'),
    path('limited', ProductLimitedView.as_view(), name='api-limited'),
    path('banners', BannerListView.as_view(), name='api-banners'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:product_id>/reviews', ProductReviewsView.as_view(), name='product-reviews'),
    path('categories', CategoryListView.as_view()),
    path('sales', SaleView.as_view(), name='api-sales'),
    path('catalog', CatalogView.as_view(), name='api-catalog'),
    path('tags', TagsView.as_view(), name='api-tags'),
    path('basket', BasketView.as_view(), name='api-basket'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
