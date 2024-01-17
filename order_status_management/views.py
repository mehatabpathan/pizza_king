from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import Http404
from checkout.models import Order


@login_required
def orders(request, status):
    """
    A view to show all orders with a given status.
    Permission required to access this view.
    """
    is_worker = request.user.groups.filter(name='Worker').exists()

    if not (is_worker or request.user.is_superuser):
        raise Http404("Resource does not exist")

    orders = Order.objects.filter(
        progress__status=status,
        progress__is_active=True).order_by('created_at')

    return render(request,
                  'order_status_management/orders.html',
                  {'active_link': 'orders',
                   'orders': orders,
                   'status': status})


@login_required
def proceed(request, order_number):
    """
    A view to proceed an order to the next status.
    Permission required to access this view.
    """
    is_worker = request.user.groups.filter(name='Worker').exists()

    if not (is_worker or request.user.is_superuser):
        raise Http404("Resource does not exist")

    order = Order.objects.get(order_number=order_number)
    prev_status = order.progress.status

    if prev_status == 'new':
        order.progress.status = 'accepted'
        order.progress.accepted_at = timezone.now()
    elif prev_status == 'accepted':
        order.progress.status = 'being_cooked'
        order.progress.start_cooking_at = timezone.now()
    elif prev_status == 'being_cooked':
        order.progress.status = 'being_prepared'
        order.progress.start_preparing_at = timezone.now()
    elif prev_status == 'being_prepared':
        order.progress.status = 'being_delivered'
        order.progress.start_delivering_at = timezone.now()
    elif prev_status == 'being_delivered':
        order.progress.status = 'completed'
        order.progress.completed_at = timezone.now()
    elif prev_status == 'completed':
        order.progress.is_active = False
    order.progress.save()
    return redirect('orders', prev_status)