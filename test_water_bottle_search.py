#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_best_products

# Test the search for "water bottle"
print("Testing search for 'water bottle'...")
products = get_best_products("water bottle")

print(f"Found {len(products)} products:")
for i, product in enumerate(products, 1):
    print(f"{i}. {product.name} - {product.category}")

print("\n" + "="*50)

# Test the search for "I want water bottle"
print("Testing search for 'I want water bottle'...")
products = get_best_products("I want water bottle")

print(f"Found {len(products)} products:")
for i, product in enumerate(products, 1):
    print(f"{i}. {product.name} - {product.category}")
