from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views
router = DefaultRouter()
router.register('', api_views.ClienteViewSet, basename='cliente')
urlpatterns = [path('', include(router.urls))]
