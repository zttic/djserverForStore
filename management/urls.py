from django.urls import path, include
from management import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', views.ProductViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'unit', views.UnitViewSet)
router.register(r'register', views.RegisterViewSet)
# router.register(r'addcategory', views.AddCategoryViewSet)
# router.register(r'login', views.LoginViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginViewSet.as_view(), name='login'),
    path('logout/', views.LogoutViewSet.as_view(), name='logout'),
    path('upload-image-to-cos/', views.UploadImageToCOSViewSet, name='upload-image-to-cos'),
    path('delete-image-from-cos/', views.DeleteImageFromCOSViewSet.as_view(), name='delete-image-from-cos'),
    path('check-session/', views.CheckSessionViewSet.as_view(), name='check-session'),
]
