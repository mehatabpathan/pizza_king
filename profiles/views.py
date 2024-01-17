from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)
    form = UserProfileForm(instance=profile)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Profile updated successfully')
        else:
            messages.error(
                request,
                'Update failed. Please ensure the form is valid.')

    orders = profile.orders.all().order_by('-created_at')
    template = 'profiles/profile.html'
    context = {
        'active_link': 'profile',
        'form': form,
        'orders': orders,
    }

    return render(request, template, context)


@login_required
def order_history(request, order_number):
    """ Display the user's selected order. """
    order = get_object_or_404(Order, order_number=order_number)
    is_user = request.user == order.user_profile.user
    timestamp = int(order.progress.new_at.timestamp())

    if not is_user:
        raise Http404("Resource does not exist")

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
        'timestamp': timestamp,
    }

    return render(request, template, context)