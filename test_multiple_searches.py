#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_best_products

test_queries = [
    "water bottle",
    "jacket",
    "shoes",
    "watch",
    "bag"
]

for query in test_queries:
    print(f"\nTesting search for '{query}'...")
    products = get_best_products(query)
    
    print(f"Found {len(products)} products:")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product.name} - {product.category}")
    
    print("-" * 50)
