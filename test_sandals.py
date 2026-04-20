import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.models import Product

# Test if sandals product exists
sandals_products = Product.objects.filter(name__icontains='sandals')
print(f"Found {sandals_products.count()} products with 'sandals' in name:")
for product in sandals_products:
    print(f"- {product.name} (activity: {product.activity_tag}, temp: {product.temp_category})")

# Test scoring manually
message = "i want sandals"
print(f"\nTesting message: '{message}'")

for product in Product.objects.all()[:10]:  # Test first 10 products
    if 'sandals' in product.name.lower():
        print(f"✓ Found sandals: {product.name}")
    else:
        print(f"- Other: {product.name}")
