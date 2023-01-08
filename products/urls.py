from django.urls import path

from products.views import (ProductsListView, basket_add, basket_down,
                            basket_remove)

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('page/<int:page>/', ProductsListView.as_view(), name='paginator'),
    path('category/<int:category_id>/', ProductsListView.as_view(), name='category'),
    path('category/<int:category_id>/page/<int:page>/',
         ProductsListView.as_view(), name='category_paginator'),
    path('baskets/add/<int:product_id>/', basket_add, name='basket_add'),
    path('baskets/down/<int:product_id>/', basket_down, name='basket_down'),
    path('baskets/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
]
