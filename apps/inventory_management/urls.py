from django.urls import path
from . import views

urlpatterns = [
    # Drink URLs
    path('', views.drink_list, name='drink_list'),
    path('detail/<int:pk>/', views.drink_detail, name='drink_detail'),
    path('create/', views.drink_create, name='drink_create'),
    path('update/<int:pk>/', views.drink_update, name='drink_update'),
    path('delete/<int:pk>/', views.drink_delete, name='drink_delete'),
    path('add_stock/', views.add_stock, name='add_stock'),
    path('reduce_stock/', views.reduce_stock, name='reduce_stock'),
 
]

