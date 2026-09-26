"""
NovaCart – Database Seeder & Mock Asset Generator
Creates realistic demo products with clean images and test user credentials with Indian Rupee (₹) pricing.
"""

import os
import sys
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
import django
django.setup()

from django.contrib.auth.models import User
from store.models import Product

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products')
os.makedirs(MEDIA_DIR, exist_ok=True)

def generate_product_image(filename, title, category, bg_color1, bg_color2, icon_emoji):
    """
    Generates a sleek, high-resolution product showcase image with gradients and icons.
    """
    width, height = 600, 600
    img = Image.new('RGB', (width, height), bg_color1)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(bg_color1[0] * (1 - ratio) + bg_color2[0] * ratio)
        g = int(bg_color1[1] * (1 - ratio) + bg_color2[1] * ratio)
        b = int(bg_color1[2] * (1 - ratio) + bg_color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    card_margin = 35
    card_shape = [
        (card_margin, card_margin),
        (width - card_margin, height - card_margin)
    ]
    draw.rounded_rectangle(card_shape, radius=24, fill=(255, 255, 255, 25), outline=(255, 255, 255, 70), width=2)

    pill_shape = [(60, 60), (220, 95)]
    draw.rounded_rectangle(pill_shape, radius=16, fill=(0, 0, 0, 80))
    
    try:
        font_cat = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_icon = ImageFont.truetype("seguiemj.ttf", 90)
    except Exception:
        font_cat = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_icon = ImageFont.load_default()

    draw.text((75, 70), f"● {category.upper()}", fill=(220, 230, 255), font=font_cat)
    draw.text((width // 2 - 50, height // 2 - 80), icon_emoji, fill=(255, 255, 255), font=font_icon)
    draw.text((60, height - 120), title, fill=(255, 255, 255), font=font_title)
    draw.text((60, height - 80), "NovaCart Official Verified Product", fill=(200, 210, 230), font=font_cat)

    filepath = os.path.join(MEDIA_DIR, filename)
    img.save(filepath, format='PNG', quality=95)
    print(f"Generated asset: {filepath}")
    return f"products/{filename}"


SAMPLE_PRODUCTS = [
    {
        "name": "Steel Water Bottle",
        "category": "Drinkware",
        "description": "Insulated double-wall stainless steel bottle that keeps drinks icy cold for 24 hours or piping hot for 12 hours. Sweat-proof powder coat finish.",
        "price": Decimal("899.00"),
        "stock": 25,
        "filename": "steel_water_bottle.png",
        "bg1": (15, 76, 129),
        "bg2": (56, 189, 248),
        "icon": "🍶"
    },
    {
        "name": "Wireless Headphones",
        "category": "Audio Gear",
        "description": "Over-ear wireless headphones with crisp, balanced sound, active hybrid noise cancellation, and ergonomic memory-foam ear cushions.",
        "price": Decimal("4999.00"),
        "stock": 15,
        "filename": "wireless_headphones.png",
        "bg1": (30, 27, 75),
        "bg2": (99, 102, 241),
        "icon": "🎧"
    },
    {
        "name": "Canvas Tote Bag",
        "category": "Fashion & Travel",
        "description": "Durable heavy-duty organic canvas tote with reinforced shoulder straps and interior zippered pockets, perfect for daily errands and travel.",
        "price": Decimal("1299.00"),
        "stock": 0,
        "filename": "canvas_tote_bag.png",
        "bg1": (120, 53, 15),
        "bg2": (217, 119, 6),
        "icon": "👜"
    },
    {
        "name": "Classic Watch",
        "category": "Accessories",
        "description": "A minimal analog timepiece featuring aerospace-grade steel casing, sapphire scratch-resistant crystal glass, and a genuine Italian leather strap.",
        "price": Decimal("3499.00"),
        "stock": 2,
        "filename": "classic_watch.png",
        "bg1": (15, 23, 42),
        "bg2": (71, 85, 105),
        "icon": "⌚"
    },
    {
        "name": "Performance Running Shoes",
        "category": "Footwear",
        "description": "Lightweight high-rebound responsive foam running shoes with breathable knit mesh upper and carbon-rubber traction outsole.",
        "price": Decimal("2799.00"),
        "stock": 14,
        "filename": "running_shoes.png",
        "bg1": (136, 19, 55),
        "bg2": (244, 63, 94),
        "icon": "👟"
    },
    {
        "name": "KeyCraft Mechanical Keyboard",
        "category": "Tech & Desk",
        "description": "75% compact layout featuring hot-swappable tactile switches, gasket mount acoustic dampening, custom PBT keycaps, and per-key RGB illumination.",
        "price": Decimal("3999.00"),
        "stock": 8,
        "filename": "keycraft_keyboard.png",
        "bg1": (49, 16, 66),
        "bg2": (139, 92, 246),
        "icon": "⌨️"
    },
    {
        "name": "ErgoPro Smart Desk Lamp",
        "category": "Home Office",
        "description": "Architectural LED task lamp with stepless color temperature adjustment, circadian auto-dimming, and an integrated 15W Qi wireless fast-charging pad.",
        "price": Decimal("1899.00"),
        "stock": 20,
        "filename": "ergopro_lamp.png",
        "bg1": (20, 83, 45),
        "bg2": (16, 185, 129),
        "icon": "💡"
    },
    {
        "name": "SoundSphere 360 Portable Speaker",
        "category": "Audio Gear",
        "description": "Omnidirectional 360-degree sound with rich punchy bass, IP67 dustproof and waterproof build, and up to 24 hours of non-stop playback on a single charge.",
        "price": Decimal("2499.00"),
        "stock": 18,
        "filename": "soundsphere_speaker.png",
        "bg1": (14, 116, 144),
        "bg2": (6, 182, 212),
        "icon": "🔊"
    }
]


def seed_database():
    print("Beginning NovaCart database population & asset generation...")

    # 1. Create or verify Superuser
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@novacart.com", "admin123")
        print("Superuser created: admin / admin123")
    else:
        user = User.objects.get(username="admin")
        user.set_password("admin123")
        user.save()
        print("Superuser verified: admin / admin123")

    # 2. Create demo customer
    if not User.objects.filter(username="john_doe").exists():
        User.objects.create_user("john_doe", "john@example.com", "password123")
        print("Demo customer created: john_doe / password123")

    # 3. Seed Products
    for item in SAMPLE_PRODUCTS:
        rel_path = generate_product_image(
            item["filename"],
            item["name"],
            item["category"],
            item["bg1"],
            item["bg2"],
            item["icon"]
        )

        product, created = Product.objects.update_or_create(
            name=item["name"],
            defaults={
                "description": item["description"],
                "price": item["price"],
                "stock": item["stock"],
                "image": rel_path
            }
        )
        action = "Created" if created else "Updated"
        print(f"{action} product: {product.name} (Rs. {product.price}, Stock: {product.stock})")

    print(f"\nSeeding complete! Total products in catalog: {Product.objects.count()}")

if __name__ == "__main__":
    seed_database()
