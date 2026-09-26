from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from .models import Product, Order, OrderItem


def home(request):
    """
    Renders the modern home page with hero section and featured products from SQLite DB.
    """
    products = Product.objects.all()
    return render(request, 'store/home.html', {
        'products': products
    })


def product_detail(request, product_id):
    """
    Renders the rich product details page.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    in_cart_qty = cart.get(str(product.id), 0)
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'in_cart_qty': in_cart_qty,
    })


def cart_view(request):
    """
    Displays the shopping cart stored in Django session.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = Decimal('0.00')

    # Fetch products and calculate item totals
    if cart:
        product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {p.id: p for p in products}

        for pid_str, qty in list(cart.items()):
            if not pid_str.isdigit():
                continue
            pid = int(pid_str)
            product = product_dict.get(pid)
            if product:
                qty = int(qty)
                # Adjust if quantity in cart exceeds current available stock
                if qty > product.stock and product.stock > 0:
                    qty = product.stock
                    cart[pid_str] = qty
                    request.session.modified = True

                item_total = product.price * qty
                grand_total += item_total
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'item_total': item_total,
                    'max_stock': product.stock
                })
            else:
                # Remove stale product from session cart
                del cart[pid_str]
                request.session.modified = True

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })


def add_to_cart(request, product_id):
    """
    Adds a product to the session cart with quantity & stock validation.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Extract quantity from POST or GET
    quantity = 1
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

    if quantity < 1:
        quantity = 1

    cart = request.session.get('cart', {})
    pid_str = str(product.id)
    current_qty = cart.get(pid_str, 0)
    new_qty = current_qty + quantity

    if new_qty > product.stock:
        cart[pid_str] = product.stock
        messages.warning(request, f"Only {product.stock} units available for '{product.name}'. Cart quantity adjusted to maximum available stock.")
    else:
        cart[pid_str] = new_qty
        messages.success(request, f"Added {quantity}x '{product.name}' to your cart!")

    request.session['cart'] = cart
    request.session.modified = True

    # Redirect to cart or referrer
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url == 'cart':
        return redirect('cart')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def update_cart_quantity(request, product_id):
    """
    Updates the quantity of a product in the session cart (increase/decrease/direct set).
    """
    if request.method != 'POST':
        return redirect('cart')

    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid_str = str(product.id)

    if pid_str not in cart:
        messages.error(request, "Product not found in cart.")
        return redirect('cart')

    action = request.POST.get('action')
    current_qty = cart[pid_str]

    if action == 'increase':
        if current_qty < product.stock:
            cart[pid_str] = current_qty + 1
            messages.success(request, f"Increased quantity for '{product.name}'.")
        else:
            messages.warning(request, f"Cannot add more. Maximum available stock is {product.stock}.")
    elif action == 'decrease':
        if current_qty > 1:
            cart[pid_str] = current_qty - 1
            messages.info(request, f"Decreased quantity for '{product.name}'.")
        else:
            del cart[pid_str]
            messages.info(request, f"Removed '{product.name}' from your cart.")
    elif action == 'set':
        try:
            new_qty = int(request.POST.get('quantity', 1))
            if new_qty <= 0:
                del cart[pid_str]
                messages.info(request, f"Removed '{product.name}' from your cart.")
            elif new_qty > product.stock:
                cart[pid_str] = product.stock
                messages.warning(request, f"Quantity set to maximum available stock ({product.stock}).")
            else:
                cart[pid_str] = new_qty
                messages.success(request, f"Updated quantity for '{product.name}'.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity provided.")

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


def remove_from_cart(request, product_id):
    """
    Removes a product completely from the session cart.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid_str = str(product.id)

    if pid_str in cart:
        del cart[pid_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, f"'{product.name}' removed from your cart.")
    
    return redirect('cart')


def checkout_view(request):
    """
    Checkout overview and order processing.
    Requires user login and non-empty cart.
    """
    if not request.user.is_authenticated:
        messages.info(request, "Please log in or create an account to proceed with checkout.")
        return redirect(f"{reverse('login')}?next={reverse('checkout')}")

    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty. Add products before checkout.")
        return redirect('home')

    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = Product.objects.filter(id__in=product_ids)
    product_dict = {p.id: p for p in products}

    order_items_data = []
    grand_total = Decimal('0.00')

    # Prepare and validate cart items
    for pid_str, qty in cart.items():
        if not pid_str.isdigit():
            continue
        pid = int(pid_str)
        product = product_dict.get(pid)
        if product:
            qty = int(qty)
            if qty > product.stock:
                messages.error(request, f"Requested quantity for '{product.name}' exceeds available stock ({product.stock}). Please update your cart.")
                return redirect('cart')
            
            item_total = product.price * qty
            grand_total += item_total
            order_items_data.append({
                'product': product,
                'quantity': qty,
                'price': product.price,
                'item_total': item_total,
            })

    if not order_items_data:
        messages.warning(request, "No valid items found in cart.")
        return redirect('cart')

    if request.method == 'POST':
        # Process order creation and stock deduction atomically
        with transaction.atomic():
            # Final stock check with DB lock
            for item in order_items_data:
                prod = Product.objects.select_for_update().get(id=item['product'].id)
                if prod.stock < item['quantity']:
                    messages.error(request, f"Insufficient stock for '{prod.name}'. Available: {prod.stock}.")
                    return redirect('cart')

            # Create Order
            order = Order.objects.create(
                user=request.user,
                total_amount=grand_total
            )

            # Create OrderItems and reduce stock
            for item in order_items_data:
                prod = Product.objects.get(id=item['product'].id)
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=item['quantity'],
                    price=prod.price
                )
                prod.stock -= item['quantity']
                prod.save()

            # Clear session cart
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'order_items': order_items_data,
        'grand_total': grand_total,
    })


@login_required(login_url='login')
def order_success(request, order_id):
    """
    Renders professional order success confirmation page.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {
        'order': order,
    })


def register_view(request):
    """
    User registration with validation and duplicate checks.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validations
        if not username or not password or not confirm_password:
            messages.error(request, "All required fields must be filled.")
            return render(request, 'store/register.html', {'username': username, 'email': email})

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'store/register.html', {'username': username, 'email': email})

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'store/register.html', {'username': username, 'email': email})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Please choose another.")
            return render(request, 'store/register.html', {'username': username, 'email': email})

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Registration successful! You can now log in with your credentials.")
        return redirect('login')

    return render(request, 'store/register.html')


def login_view(request):
    """
    User authentication view.
    """
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', 'home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or 'home'

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, 'store/login.html', {'username': username, 'next': next_url})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'store/login.html', {'username': username, 'next': next_url})

    return render(request, 'store/login.html', {'next': next_url})


def logout_view(request):
    """
    Logs out the user and redirects to home with message.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"Goodbye {username}! You have logged out successfully.")
    return redirect('home')
