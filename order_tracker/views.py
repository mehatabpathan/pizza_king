from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from checkout.models import Order
from .forms import OrderTrackerForm


def order_tracker(request):
    """
    A view to show the order tracker page
    This view leads to the order tracker bar
    """
    if request.method == 'POST':
        form = OrderTrackerForm(request.POST)
        if form.is_valid():
            order_number = form.cleaned_data['order_number']
            order = Order.objects.filter(order_number=order_number).exists()

            if order:
                order = Order.objects.get(order_number=order_number)
                if order.progress.is_active:
                    timestamp = int(order.progress.new_at.timestamp())
                    return redirect('order_tracker_bar',
                                    order_number=order.order_number,
                                    timestamp=timestamp)
                else:
                    messages.error(request, 'Order not found')
                    form.add_error(
                        'order_number',
                        'Please enter a valid order number.')
            else:
                messages.error(request, 'Order not found')
                form.add_error(
                    'order_number',
                    'Please enter a valid order number.')
    else:
        form = OrderTrackerForm()
    return render(request,
                  'order_tracker/order_tracker.html',
                  {'active_link': 'tracker',
                   'form': form})


def order_tracker_bar(request, order_number, timestamp):
    """
    A view to show the order tracker bar
    Order number of active order is required
    """
    order = get_object_or_404(
        Order,
        order_number=order_number,
        progress__is_active=True)

    if int(order.progress.new_at.timestamp()) != int(timestamp):
        raise Http404('Order not found')

    status = order.progress.status

    time_taken = None
    status_name = 'Pending'

    if status == 'accepted':
        status_name = 'Accepted'
    elif status == 'being_cooked':
        status_name = 'Cooking'
    elif status == 'being_prepared':
        status_name = 'Preparing'
    elif status == 'being_delivered':
        status_name = 'Delivering'
    elif status == 'completed':
        status_name = 'Delivered'
        time_taken = order.progress.completed_at - order.progress.new_at
        time_taken = time_taken.total_seconds() // 60
        time_taken = str(time_taken).split('.')[0]

    return render(
        request,
        'order_tracker/order_tracker_bar.html',
        {
            'status': status,
            'status_name': status_name,
            'order': order,
            'active_link': 'tracker',
            'time_taken': time_taken})