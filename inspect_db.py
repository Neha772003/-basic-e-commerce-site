import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Product

print("=== PRODUCTS IN DATABASE ===")
for p in Product.objects.all():
    has_img = bool(p.image)
    path_exists = False
    img_name = str(p.image) if has_img else "None"
    if has_img:
        try:
            path_exists = os.path.exists(p.image.path)
        except Exception as e:
            path_exists = False
    print(f"ID: {p.id} | Name: {p.name} | Price: {p.price} | Stock: {p.stock} | Image: {img_name} | FileExists: {path_exists}")
