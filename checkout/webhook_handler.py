from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from .forms import OrderForm
from products.models import Product, Topping
from profiles.models import UserProfile

from decimal import Decimal

import json
import time
import stripe


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)

        order_form = OrderForm({
            'full_name': shipping_details.name,
            'email': billing_details.email,
            'phone_number': shipping_details.phone,
            'street_address1': shipping_details.address.line1,
            'street_address2': shipping_details.address.line2,
            'postcode': shipping_details.address.postal_code,
        })

        if not order_form.is_valid():
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                street_address1 = shipping_details.address.line1
                street_address2 = shipping_details.address.line2
                profile.default_full_name = shipping_details.name
                profile.default_phone_number = shipping_details.phone
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_street_address1 = street_address1
                profile.default_street_address2 = street_address2
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            verified = 'SUCCESS: Verified order already in database'
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | {verified}',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_list in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    for item in item_list:
                        selec_topp = None
                        if len(item['additional_toppings']) > 0:
                            if len(item['additional_toppings']) > 1:
                                selec_topp = Topping.objects.filter(
                                    id__in=item['additional_toppings'])
                            else:
                                selec_topp = Topping.objects.filter(
                                    id=item['additional_toppings'][0])

                        t_p = 0
                        if selec_topp is not None:
                            t_p = sum(
                                int(topping.price)
                                for topping in selec_topp.all()
                            ) * item['quantity']

                        if item['size'] == '30':
                            tot_price = product.price * item['quantity']
                            lineitem_total = tot_price + t_p
                        elif item['size'] == '35':
                            t_p = t_p * Decimal(1.1)
                            p_p = product.price * Decimal(1.1)
                            lineitem_total = p_p * item['quantity'] + t_p
                        elif item['size'] == '40':
                            t_p = t_p * Decimal(1.3)
                            p_p = product.price * Decimal(1.3)
                            lineitem_total = p_p * item['quantity'] + t_p

                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                product_size=item['size'],
                                quantity=item['quantity'],
                                lineitem_total=round(lineitem_total, 2),
                            )

                            order_line_item.save()

                            if selec_topp is not None:
                                order_line_item.toppings.set(selec_topp)
                                order_line_item.save()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        verified = 'SUCCESS: Created order in webhook'
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | {verified}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)