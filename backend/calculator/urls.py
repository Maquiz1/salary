from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/calculate/', views.calculate_api, name='calculate_api'),
]
