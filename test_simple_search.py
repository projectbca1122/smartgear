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
    "shirt",
    "pants",
    "bag"
]

for query in test_queries:
    print(f"\n{'='*50}")
    print(f"Testing: '{query}'")
    print('='*50)
    
    products = get_best_products(query)
    
    print(f"Found {len(products)} products:")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product.name}")
    
    if not products:
        print("No products found")
