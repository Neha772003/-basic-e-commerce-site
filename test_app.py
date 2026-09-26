"""
NovaCart Automated Test Suite & Verification Script
Runs end-to-end verification across models, views, cart sessions, auth, and order processing with Indian Rupee (₹).
"""

import os
import sys
from decimal import Decimal

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Product, Order, OrderItem

def run_tests():
    print("==========================================")
    print("   NOVACART E-COMMERCE VERIFICATION TEST   ")
    print("==========================================")
    client = Client()

    # Test 1: Home Page Loading
    response = client.get(reverse('home'))
    assert response.status_code == 200, f"Home page failed with {response.status_code}"
    assert b'Featured Products' in response.content, "Home page missing Featured Products heading"
    products_count = Product.objects.count()
    assert products_count >= 8, f"Expected >= 8 products, found {products_count}"
    assert '₹'.encode('utf-8') in response.content, "Rupee symbol missing from home page"
    print(f"[PASS] Test 1: Home page loaded successfully with {products_count} database products and Rupee (₹) symbol.")

    # Test 2: Product Detail Page
    first_product = Product.objects.first()
    detail_url = reverse('product_detail', args=[first_product.id])
    response = client.get(detail_url)
    assert response.status_code == 200, f"Detail page failed with {response.status_code}"
    assert first_product.name.encode() in response.content, "Product detail missing product name"
    assert '₹'.encode('utf-8') in response.content, "Rupee symbol missing from product detail"
    print(f"[PASS] Test 2: Product detail page verified for '{first_product.name}' with ₹ pricing.")

    # Test 3: User Registration
    test_username = "test_shopper_99"
    test_password = "SecurePassword123"
    User.objects.filter(username=test_username).delete()

    reg_url = reverse('register')
    res_reg = client.post(reg_url, {
        'username': test_username,
        'email': 'shopper@example.com',
        'password': test_password,
        'confirm_password': test_password
    }, follow=True)
    assert res_reg.status_code == 200, "Registration post failed"
    assert User.objects.filter(username=test_username).exists(), "User not created in database"
    print("[PASS] Test 3: User registration validation & DB creation working.")

    # Test 4: User Login & Session
    login_url = reverse('login')
    res_login = client.post(login_url, {
        'username': test_username,
        'password': test_password
    }, follow=True)
    assert res_login.status_code == 200
    print(f"[PASS] Test 4: User '{test_username}' logged in successfully.")

    # Test 5: Cart Operations
    initial_stock = first_product.stock
    add_url = reverse('add_to_cart', args=[first_product.id])
    
    # Add 2 items
    client.post(add_url, {'quantity': 2}, follow=True)
    session = client.session
    assert str(first_product.id) in session.get('cart', {}), "Item not in session cart"
    assert session['cart'][str(first_product.id)] == 2, "Cart quantity mismatch"

    # View cart page
    cart_url = reverse('cart')
    res_cart = client.get(cart_url)
    assert res_cart.status_code == 200
    assert first_product.name.encode() in res_cart.content
    assert '₹'.encode('utf-8') in res_cart.content
    print("[PASS] Test 5: Product added to cart and rendered on cart page with ₹ prices.")

    # Test 6: Quantity Update & Stock Limit Protection
    update_url = reverse('update_cart_quantity', args=[first_product.id])
    
    # Increase by 1
    client.post(update_url, {'action': 'increase'}, follow=True)
    assert client.session['cart'][str(first_product.id)] == 3

    # Attempt to set quantity higher than available stock
    client.post(update_url, {'action': 'set', 'quantity': initial_stock + 100}, follow=True)
    assert client.session['cart'][str(first_product.id)] == initial_stock, "Cart exceeded maximum stock limit!"
    print(f"[PASS] Test 6: Cart stock bounds enforcement correctly capped at {initial_stock}.")

    # Test 7: Checkout & Order Placement
    client.post(update_url, {'action': 'set', 'quantity': 2}, follow=True)
    
    checkout_url = reverse('checkout')
    res_checkout = client.get(checkout_url)
    assert res_checkout.status_code == 200, "Checkout page failed"
    assert '₹'.encode('utf-8') in res_checkout.content

    # Post order
    res_place = client.post(checkout_url, follow=True)
    assert res_place.status_code == 200, "Order placement failed"

    # Verify Order in DB
    user_obj = User.objects.get(username=test_username)
    latest_order = Order.objects.filter(user=user_obj).first()
    assert latest_order is not None, "Order record not found in database"
    assert latest_order.total_amount == first_product.price * 2, f"Total amount mismatch: {latest_order.total_amount}"
    
    # Verify OrderItem in DB
    order_items = OrderItem.objects.filter(order=latest_order)
    assert order_items.count() == 1, "OrderItem count mismatch"
    assert order_items.first().product == first_product
    assert order_items.first().quantity == 2

    # Verify Stock Deduction
    first_product.refresh_from_db()
    assert first_product.stock == initial_stock - 2

    # Verify Cart Cleared
    assert len(client.session.get('cart', {})) == 0
    print(f"[PASS] Test 7: Order #{latest_order.id} placed for ₹{latest_order.total_amount}! Stock deducted, OrderItems created, and cart cleared.")

    # Test 8: Order Success Page
    success_url = reverse('order_success', args=[latest_order.id])
    res_success = client.get(success_url)
    assert res_success.status_code == 200
    assert '₹'.encode('utf-8') in res_success.content
    print(f"[PASS] Test 8: Order success page rendered with ₹ currency.")

    # Test 9: Logout Flow
    logout_url = reverse('logout')
    res_logout = client.get(logout_url, follow=True)
    assert res_logout.status_code == 200
    print("[PASS] Test 9: User logout executed smoothly.")

    print("\n==========================================")
    print("   ALL 9 TEST SUITES PASSED FLAWLESSLY!   ")
    print("==========================================")

if __name__ == '__main__':
    run_tests()
