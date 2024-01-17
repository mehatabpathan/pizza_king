from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import Product, Topping
from .forms import ProductForm, PizzaFilterForm, ToppingForm
from cloudinary.uploader import destroy
from .utils import configure_cloudinary


def pizza_list(request):
    """ A view to show all pizzas, including sorting and search queries """
    products = Product.objects.all()
    full_path = request.build_absolute_uri()
    query = request.GET.get('q')
    if query:
        form = PizzaFilterForm()
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
    else:
        form = PizzaFilterForm(request.GET)
        if form.is_valid():
            is_spicy = form.cleaned_data.get('is_spicy')
            is_vegetarian = form.cleaned_data.get('is_vegetarian')
            is_premium = form.cleaned_data.get('is_premium')
            is_seafood = form.cleaned_data.get('is_seafood')
            is_new = form.cleaned_data.get('is_new')

            filters = {}
            if is_spicy:
                filters['is_spicy'] = is_spicy
            if is_vegetarian:
                filters['is_vegetarian'] = is_vegetarian
            if is_premium:
                filters['is_premium'] = is_premium
            if is_seafood:
                filters['is_seafood'] = is_seafood
            if is_new:
                filters['is_new'] = is_new

            if any(filters.values()):
                products = products.filter(**filters)

    products = products.order_by('-id')
    paginator = Paginator(products, 12)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(
        request,
        'products/pizza_list.html',
        {'products': products,
         'form': form,
         'full_path': full_path,
         'active_link': 'pizza'})


def pizza_detail(request, slug):
    """
    A view to show individual pizza details
    including toppings
    """
    full_path = request.build_absolute_uri()
    pizza = Product.objects.get(slug=slug)
    toppings = Topping.objects.all()
    return render(request,
                  'products/pizza_detail.html',
                  {'product': pizza,
                   'toppings': toppings,
                   'full_path': full_path
                   })


@login_required
def add_pizza(request):
    """ Add a pizza to the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Pizza added successfully')
            return redirect(reverse('pizza_list'))
        else:
            messages.error(
                request,
                'Failed to add pizza. Please ensure the form is valid.')
    else:
        form = ProductForm()

    return render(request,
                  'products/pizza_add.html',
                  {'form': form})


@login_required
def add_topping(request):
    """ Add a topping to the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    if request.method == 'POST':
        form = ToppingForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Topping added successfully')
            return redirect('pizza_list')
        else:
            messages.error(
                request,
                'Failed to add topping. Please ensure the form is valid.')
    else:
        form = ToppingForm()

    return render(request,
                  'products/topping_add.html',
                  {'form': form})


@login_required
def edit_pizza(request, slug):
    """ Edit a pizza in the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = get_object_or_404(Product, slug=slug)
            new_image = request.FILES.get('image')
            image_clear = request.POST.get('image-clear')
            if product.image:
                if image_clear == 'on':
                    configure_cloudinary()
                    destroy(product.image.public_id)
                elif new_image:
                    configure_cloudinary()
                    destroy(product.image.public_id)
            form.save()
            messages.success(request, 'Pizza updated successfully')
            slug = slugify(form.cleaned_data.get('name'))
            return redirect('pizza_detail', slug=slug)
        else:
            messages.error(
                request,
                'Failed to update pizza. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    return render(request, 'products/pizza_edit.html', {'form': form})


@login_required
def edit_topping(request, slug):
    """ Edit a topping in the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    topping = get_object_or_404(Topping, slug=slug)

    if request.method == 'POST':
        form = ToppingForm(request.POST, request.FILES, instance=topping)
        if form.is_valid():
            topping = get_object_or_404(Topping, slug=slug)
            new_image = request.FILES.get('image')
            image_clear = request.POST.get('image-clear')
            if topping.image:
                if image_clear == 'on':
                    configure_cloudinary()
                    destroy(topping.image.public_id)
                elif new_image:
                    configure_cloudinary()
                    destroy(topping.image.public_id)
            form.save()
            messages.success(request, 'Topping updated successfully')
            return redirect('pizza_list')
        else:
            messages.error(
                request,
                'Failed to update topping. Please ensure the form is valid.')
    else:
        form = ToppingForm(instance=topping)
        messages.info(request, f'You are editing {topping.name}')

    return render(request, 'products/topping_edit.html', {'form': form})


@login_required
def delete_pizza(request, slug):
    """ Delete a pizza from the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    product = get_object_or_404(Product, slug=slug)

    if product.image:
        configure_cloudinary()
        destroy(product.image.public_id)
    product.delete()
    messages.success(request, 'Pizza deleted!')
    return redirect('pizza_list')


@login_required
def delete_topping(request, slug):
    """ Delete a topping from the store (admin only)"""
    if not request.user.is_superuser:
        return redirect(reverse('pizza_list'))

    topping = get_object_or_404(Topping, slug=slug)

    if topping.image:
        configure_cloudinary()
        destroy(topping.image.public_id)
    topping.delete()
    messages.success(request, 'Topping deleted!')
    return redirect('pizza_list')