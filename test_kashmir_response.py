#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_best_products, generate_smart_response

# Test Kashmir weather response
print("Testing: I'm going to Kashmir so I want some jackets.")

# Mock weather info for Kashmir
weather_info = {
    'success': True,
    'temperature': -5,
    'description': 'snowy',
    'location': 'Kashmir'
}

products = get_best_products("I'm going to Kashmir so I want some jackets.")
print(f"Products found: {[p.name for p in products]}")

response = generate_smart_response("I'm going to Kashmir so I want some jackets.", weather_info)
print(f"Smart response: {response}")
