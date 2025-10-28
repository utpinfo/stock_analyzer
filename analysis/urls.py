from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('stocks/<int:id>/', views.stock_detail, name='stock_detail'),
]
