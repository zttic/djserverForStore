from django.urls import path, include
from weapp import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'category', views.CategoryViewSet)
router.register(r'productDetails', views.ItemofProductViewSet)
router.register(r'unit', views.UnitViewSet, basename='unit')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'auth', views.AuthViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
