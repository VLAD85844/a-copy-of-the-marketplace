from django.urls import path
from .views import ProductPopularView, ProductLimitedView, CategoryListView

urlpatterns = [
    path('products/popular', ProductPopularView.as_view(), name='api-popular'),
    path('products/limited', ProductLimitedView.as_view(), name='api-limited'),
    path('categories', CategoryListView.as_view(), name='api-categories'),
]
