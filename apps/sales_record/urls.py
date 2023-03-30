from django.urls import path
from . import views

urlpatterns = [
    # # Sale URLs
    path('', views.sale_list, name='sale_list'),
    path('create/', views.sale_create, name='sale_create'),
    path('<int:pk>/update/', views.sale_update, name='sale_update'),
    path('<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    # # Sale Report URL
    path('sale_report/', views.sale_report, name='sale_report'),
    # debt URLs
    path('debt_list', views.debt_list, name='debt_list'),
    path('debts/<str:status>/', views.debt_list, name='debt_list'),
    path('clear-debt/<int:pk>/', views.clear_debt, name='clear_debt'),
    path('<int:pk>/debt_delete/', views.debt_delete, name='debt_delete'),
]

