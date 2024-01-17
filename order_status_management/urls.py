from django.urls import path
from . import views

urlpatterns = [
    path('orders/<status>', views.orders, name='orders'),
    path('proceed/<order_number>', views.proceed, name='proceed'),
    ]