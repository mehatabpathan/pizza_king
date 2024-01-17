from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_tracker, name='order_tracker'),
    path('<order_number>/<timestamp>/',
         views.order_tracker_bar, name='order_tracker_bar'),
    ]