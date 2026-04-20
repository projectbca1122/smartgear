import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.models import Product

# Test scoring function
def test_scoring():
    message = "i want sandals"
    
    # Test scoring for sandals product
    sandals_product = Product.objects.get(name__icontains='sandals')
    print(f"Testing product: {sandals_product.name}")
    
    # Simulate word matching
    user_words = message.lower().split()
    product_words = sandals_product.name.lower().split()
    
    print(f"User words: {user_words}")
    print(f"Product words: {product_words}")
    
    # Check matches
    word_matches = 0
    for user_word in user_words:
        for product_word in product_words:
            if user_word == product_word or user_word in product_word or product_word in user_word:
                word_matches += 1
                print(f"MATCH: '{user_word}' matches '{product_word}'")
    
    print(f"Total word matches: {word_matches}")
    print(f"Score from word matches: {word_matches * 25}")

if __name__ == "__main__":
    test_scoring()
