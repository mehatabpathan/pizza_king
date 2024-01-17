from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from .models import Order, OrderLineItem
from products.models import Product, Topping
from bag.contexts import bag_contents
from decimal import Decimal

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    A view to cache the checkout data
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    A view to return the checkout page,
    handle the checkout form and stripe payments
    calls the cache_checkout_data view,
    calculates the total price of the order
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'postcode': request.POST['postcode'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
        }

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_list in bag.items():
                product = Product.objects.get(id=item_id)
                for item in item_list:
                    try:
                        selec_topp = None
                        if len(item['additional_toppings']) > 0:
                            if len(item['additional_toppings']) > 1:
                                selec_topp = (
                                    Topping.objects.filter(
                                        id__in=item['additional_toppings'])
                                        )
                            else:
                                selec_topp = (
                                    Topping.objects.filter(
                                        id=item['additional_toppings'][0])
                                        )

                        tp_p = 0
                        if selec_topp is not None:
                            tp_p = sum(
                                int(topping.price)
                                for topping in selec_topp.all()
                            ) * item['quantity']

                        if item['size'] == '30':
                            item_q = item['quantity']
                            item_total = product.price * item_q + tp_p
                        elif item['size'] == '35':
                            tp_p = tp_p * Decimal(1.1)
                            p_pr = product.price * Decimal(1.1)
                            item_total = (
                                p_pr * item['quantity'] + tp_p
                                )
                        elif item['size'] == '40':
                            tp_p = tp_p * Decimal(1.3)
                            p_pr = product.price * Decimal(1.3)
                            item_total = (
                                p_pr * item['quantity'] + tp_p
                                )

                        try:
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                product_size=item['size'],
                                quantity=item['quantity'],
                                lineitem_total=round(item_total, 2),
                            )

                            order_line_item.save()

                            if selec_topp is not None:
                                order_line_item.toppings.set(selec_topp)
                                order_line_item.save()
                        except Exception as e:
                            messages.error(request, f'An error occurred \
                                Please try again later. {e}')
                            order.delete()
                            return redirect(reverse('view_bag'))

                    except Product.DoesNotExist:
                        messages.error(request, (
                            "A product in your bag wasn't found."
                            "Please call us for assistance!")
                        )
                        order.delete()
                        return redirect(reverse('view_bag'))
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag")
            return redirect(reverse('pizza_list'))

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.default_full_name,
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'postcode': profile.default_postcode,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    timestamp = int(order.progress.new_at.timestamp())

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_full_name': order.full_name,
                'default_phone_number': order.phone_number,
                'default_postcode': order.postcode,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'timestamp': timestamp,
    }

    return render(request, template, context)