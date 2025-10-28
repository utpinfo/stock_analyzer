from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stocks/', views.stocks, name='stocks'),
    path('stocks/<int:id>/', views.stock_detail, name='stock_detail'),
]
