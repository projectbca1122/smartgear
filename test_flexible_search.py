#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_best_products

test_queries = [
    "bag",
    "bags", 
    "bottle",
    "bottles",
    "show me bag",
    "show me bags",
    "show me bottle.",
    "show me bottles.",
    "jacket",
    "jackets"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Testing: '{query}'")
    print('='*60)
    
    products = get_best_products(query)
    
    if products:
        print(f"Found {len(products)} products:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
    else:
        print("No products found")
