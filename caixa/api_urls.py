from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views
router = DefaultRouter()
router.register('', api_views.CaixaViewSet, basename='caixa')
from django.urls import include
urlpatterns = [path('', include(router.urls))]
