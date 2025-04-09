from django.urls import path
from .views import (
    HomeView,
    CatalogView,
    ProductDetailView,
    ProductPopularAPIView,
    ProductLimitedAPIView,
    CategoryListAPIView,
    BannerListAPIView,
    BasketAPIView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('api/products/popular/', ProductPopularAPIView.as_view(), name='api-popular'),
    path('api/products/limited/', ProductLimitedAPIView.as_view(), name='api-limited'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api-categories'),
    path('api/banners/', BannerListAPIView.as_view(), name='api-banners'),
    path('api/basket/', BasketAPIView.as_view(), name='api-basket'),
]
