#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import generate_chat_response, get_best_products

# Test chat response with bottle search
print("Testing chat response for 'I want bottle.'")
products = get_best_products("I want bottle.")

print(f"Products found: {[p.name for p in products]}")

# Mock weather info
weather_info = {
    'success': True,
    'temperature': 25,
    'description': 'sunny',
    'location': 'your location'
}

response = generate_chat_response("I want bottle.", weather_info, products)
print(f"Chat response: {response}")

print("\n" + "="*60)

# Test chat response with bag search
print("Testing chat response for 'show me bags'")
products = get_best_products("show me bags")

print(f"Products found: {[p.name for p in products]}")

response = generate_chat_response("show me bags", weather_info, products)
print(f"Chat response: {response}")
