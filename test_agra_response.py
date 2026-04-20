#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_best_products, generate_chat_response

# Test Agra weather response
print("Testing: I am going to Agra so I want some pants.")

# Mock weather info for Agra
weather_info = {
    'success': True,
    'temperature': 35,
    'description': 'hot',
    'location': 'Agra'
}

products = get_best_products("I am going to Agra so I want some pants.")
print(f"Products found: {[p.name for p in products]}")

response = generate_chat_response("I am going to Agra so I want some pants.", weather_info, products)
print(f"Chat response: {response}")
