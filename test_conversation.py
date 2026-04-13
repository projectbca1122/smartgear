#!/usr/bin/env python
"""
Test the conversational AI flow
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.views import get_ai_response

# Test conversations
test_cases = [
    "Hi my name is Parth",
    "Going Kashmir", 
    "What should I wear there?",
    "show me jackets"
]

print("🤖 TESTING CONVERSATIONAL AI FLOW")
print("=" * 50)

for i, message in enumerate(test_cases, 1):
    print(f"\n👤 USER {i}: {message}")
    response = get_ai_response(message)
    print(f"🤖 AI {i}: {response}")
    print("-" * 30)
