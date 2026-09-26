from .models import Product

def cart_context(request):
    """
    Context processor to inject cart_total_items into all templates.
    Cart session structure: request.session['cart'] = {'product_id_str': quantity_int}
    """
    cart = request.session.get('cart', {})
    total_items = 0
    
    if isinstance(cart, dict):
        for pid, qty in cart.items():
            if isinstance(qty, int):
                total_items += qty
            elif isinstance(qty, str) and qty.isdigit():
                total_items += int(qty)
                
    return {
        'cart_total_items': total_items,
    }
