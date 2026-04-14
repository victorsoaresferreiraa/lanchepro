from django.urls import path
from . import api_views
urlpatterns = [
    path('metricas/', api_views.metricas, name='metricas'),
]
