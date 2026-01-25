from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PurchaseRequestViewSet
from . import views

router = DefaultRouter()
router.register(r'purchase-requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'customers', views.CustomerViewSet, basename='customer')

urlpatterns = [
    path("", views.home, name="home"),
    
    path('api/', include(router.urls)),

    path('request/item/', views.purchase_request, name='request_item'),
    path("requests/", views.requests_list_view, name="requests_list"),
    path("requests/<int:pk>/status/<str:status>/", views.change_request_status, name="change_request_status"),
    path("my-requests/", views.my_requests_view, name="my_requests"),

    path("create/supplier/", views.CreateSupplierViewSet.as_view({'post': 'create'}), name="create_supplier"),
]