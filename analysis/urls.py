from django.urls import path
from . import views

urlpatterns = [
    path('', views.stocks, name='home'),
    path('stocks/', views.stocks, name='stocks'),
    path('analysis/', views.analysis, name='analysis'),
    path('stocks/<int:id>/', views.stock_detail, name='stock_detail'),
]
