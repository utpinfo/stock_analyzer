from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.stocks, name='home'),
    path('stocks/', views.stocks, name='stocks'),
    path('analysis/', views.analysis, name='analysis'),
    path('update_stock/<int:stock_id>/', views.update_stock, name='update_stock'),

]
