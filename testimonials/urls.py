from django.urls import path
from . import views

urlpatterns = [
    path('', views.testimonials_view, name='testimonials'),
    path('add_testimonial/', views.add_testimonial, name='add_testimonial'),
    path('approve_testimonial/<int:testimonial_id>/',
         views.approve_testimonial, name='approve_testimonial'),
    path('delete_testimonial/<int:testimonial_id>/',
         views.delete_testimonial, name='delete_testimonial'),
    path('not_approved_testimonials/',
         views.view_not_approved_testimonials,
         name='not_approved_testimonials'),
]