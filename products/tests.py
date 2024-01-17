from django.urls import path
from . import views

urlpatterns = [
    path('', views.pizza_list, name='pizza_list'),
    path('pizza_detail/<slug:slug>',
         views.pizza_detail, name='pizza_detail'),
    path('add_pizza',
         views.add_pizza, name='add_pizza'),
    path('add_topping',
         views.add_topping, name='add_topping'),
    path('edit_pizza/<slug:slug>',
         views.edit_pizza, name='edit_pizza'),
    path('edit_topping/<slug:slug>',
         views.edit_topping, name='edit_topping'),
    path('delete_pizza/<slug:slug>',
         views.delete_pizza, name='delete_pizza'),
    path('delete_topping/<slug:slug>',
         views.delete_topping, name='delete_topping'),
    ]