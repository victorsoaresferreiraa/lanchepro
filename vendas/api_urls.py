from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views
router = DefaultRouter()
router.register('', api_views.VendaViewSet, basename='venda')
urlpatterns = [path('', include(router.urls))]
