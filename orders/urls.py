from django.contrib.auth.decorators import login_required
from django.urls import path

from orders.views import (CanceledTemplateView, OrderCreateView,
                          SuccessTemplateView)

app_name = 'orders'

urlpatterns = [
    path('create/', login_required(OrderCreateView.as_view()), name='order_create'),
    path('order-success/', SuccessTemplateView.as_view(), name='order_success'),
    path('order-canceled/', CanceledTemplateView.as_view(), name='order_canceled'),
]
