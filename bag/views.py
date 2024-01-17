from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
from products.models import Topping
import uuid


def view_bag(request):
    """ A view that renders the cart page """

    return render(request, 'bag/bag.html', {'active_link': 'bag'})


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    if request.method == 'POST':
        size = request.POST.get('selected_size')
        additional_toppings = request.POST.get('additional_toppings')
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})
        sorted_toppings_list = []
        if additional_toppings:
            additional_toppings_list = additional_toppings.split(',')
            if len(additional_toppings_list) > 7:
                messages.warning(request,
                                 "You can only add up to 7 toppings")
                if 'bag' in request.session:
                    del request.session['bag']
                return redirect(redirect_url)

            add_topp = Topping.objects.filter(id__in=additional_toppings_list)
            if len(add_topp) != len(additional_toppings_list):
                if 'bag' in request.session:
                    del request.session['bag']
                messages.error(request,
                               "Some additional toppings do not exist.")
                return redirect(redirect_url)
            sorted_toppings_list = sorted(additional_toppings_list)

        if item_id in bag:
            size_p = [pizza for pizza in bag[item_id] if pizza['size'] == size]
            if len(size_p) > 0:
                flag = True
                for pizza in size_p:
                    sorted_toppings = sorted(pizza['additional_toppings'])
                    if sorted_toppings == sorted_toppings_list:
                        if pizza['quantity'] > 14:
                            messages.error(request,
                                           "Maximum is 15 pizzas of one type")
                            if 'bag' in request.session:
                                del request.session['bag']
                            return redirect(redirect_url)

                        pizza['quantity'] += 1
                        flag = False
                        break
                if flag:
                    bag[item_id].append({
                        'id': str(uuid.uuid4()),
                        'size': size,
                        'additional_toppings': sorted_toppings_list,
                        'quantity': 1
                    })
            else:
                bag[item_id].append({
                    'id': str(uuid.uuid4()),
                    'size': size,
                    'additional_toppings': sorted_toppings_list,
                    'quantity': 1
                })
        else:
            bag[item_id] = [{
                'id': str(uuid.uuid4()),
                'size': size,
                'additional_toppings': sorted_toppings_list,
                'quantity': 1
            }]
        messages.success(request, f'Pizza added to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    quantity = int(request.POST.get('quantity'))

    if quantity > 15:
        messages.warning(request, "Maximum is 15 pizzas of one type")
        if 'bag' in request.session:
            del request.session['bag']
        return redirect(reverse('pizza_list'))

    if quantity < 1:
        messages.warning(request, "Cannot have less than 1 pizza")
        if 'bag' in request.session:
            del request.session['bag']
        return redirect(reverse('pizza_list'))

    id = request.POST.get('id')
    bag = request.session.get('bag', {})
    for pizza in bag[item_id]:
        if pizza['id'] == id:
            pizza['quantity'] = quantity

    request.session['bag'] = bag
    messages.info(request, f'Updated pizza quantity to {quantity}')
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id, id):
    """Remove the item from the shopping bag"""

    try:
        bag = request.session.get('bag', {})
        bag[item_id] = [pizza for pizza in bag[item_id] if pizza['id'] != id]

        request.session['bag'] = bag
        messages.info(request, f'Pizza removed from your bag')
        return redirect(reverse('view_bag'))

    except Exception as e:
        return HttpResponse(status=500)