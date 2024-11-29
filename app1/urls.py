from django.urls import path
from .views import (
    RegisterAPIView, 
    LoginAPIView, 
    DashboardAPIView,
    ProductCreateAPIView, 
    ProductRetrieveAPIView, 
    ProductUpdateAPIView, 
    ProductDeleteAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    path('products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductRetrieveAPIView.as_view(), name='product-retrieve'),
    path('products/<int:pk>/update/', ProductUpdateAPIView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),
]
