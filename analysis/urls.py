from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.stocks, name='home'),
    path('stocks/', views.stocks, name='stocks'),
    path('analysis/', views.analysis, name='analysis'),
    path('stocks/<int:id>/', views.stock_detail, name='stock_detail'),
    path('edit_stock/<int:stock_id>/', views.edit_stock, name='edit_stock'),
    path('update_stock/<int:stock_id>/', views.update_stock, name='update_stock'),

]
