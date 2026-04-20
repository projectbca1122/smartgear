#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.models import Product

print('Final database summary:')
print(f'Total products: {Product.objects.count()}')
print(f'Products with photos: {Product.objects.exclude(image_url__isnull=True).exclude(image_url="").count()}')

print('\nNew accessories added:')
accessories = Product.objects.filter(category='Accessories').order_by('-id')[:10]
for a in accessories:
    print(f'- {a.name}: ₹{a.price}')

print('\nSample products with photos:')
sample_products = Product.objects.all()[:5]
for p in sample_products:
    print(f'- {p.name}: {p.image_url[:50]}...' if p.image_url else f'- {p.name}: No photo')
