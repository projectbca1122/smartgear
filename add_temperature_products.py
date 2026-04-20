import os
import django
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.models import Product

def add_moderate_products():
    """Add 20 moderate temperature products"""
    moderate_products = [
        {
            'name': 'Cotton T-Shirt - Summer Breeze',
            'description': 'Lightweight cotton t-shirt perfect for moderate weather',
            'category': 'Tops',
            'price': 29.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, mumbai, delhi, pune, hyderabad',
            'priority_score': 5
        },
        {
            'name': 'Denim Jacket - Classic',
            'description': 'Classic denim jacket for moderate temperatures',
            'category': 'Outerwear',
            'price': 89.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, chennai, kolkata',
            'priority_score': 8
        },
        {
            'name': 'Linen Shirt - Beach Style',
            'description': 'Breathable linen shirt for moderate climates',
            'category': 'Shirts',
            'price': 45.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'goa, mumbai, chennai, kerala, bangalore',
            'priority_score': 6
        },
        {
            'name': 'Light Hoodie - Comfort Fit',
            'description': 'Lightweight hoodie for moderate weather',
            'category': 'Outerwear',
            'price': 59.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, delhi, hyderabad, mumbai',
            'priority_score': 7
        },
        {
            'name': 'Chino Pants - Slim Fit',
            'description': 'Comfortable chino pants for moderate temperatures',
            'category': 'Bottoms',
            'price': 79.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 6
        },
        {
            'name': 'Polo Shirt - Sport Edition',
            'description': 'Sporty polo shirt for moderate weather',
            'category': 'Tops',
            'price': 39.99,
            'activity_tag': 'sports',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 5
        },
        {
            'name': 'Casual Blazer - Modern',
            'description': 'Modern blazer for moderate business casual',
            'category': 'Outerwear',
            'price': 129.99,
            'activity_tag': 'business',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 9
        },
        {
            'name': 'Track Pants - Athletic',
            'description': 'Athletic track pants for moderate workouts',
            'category': 'Bottoms',
            'price': 49.99,
            'activity_tag': 'gym',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 6
        },
        {
            'name': 'Cotton Kurta - Traditional',
            'description': 'Traditional cotton kurta for moderate weather',
            'category': 'Ethnic Wear',
            'price': 69.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 7
        },
        {
            'name': 'Light Cardigan - Cozy',
            'description': 'Light cardigan for moderate evenings',
            'category': 'Outerwear',
            'price': 54.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 6
        },
        {
            'name': 'Sports Shorts - Active',
            'description': 'Active sports shorts for moderate weather',
            'category': 'Bottoms',
            'price': 34.99,
            'activity_tag': 'sports',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 5
        },
        {
            'name': 'Cotton Saree - Elegant',
            'description': 'Elegant cotton saree for moderate weather',
            'category': 'Ethnic Wear',
            'price': 89.99,
            'activity_tag': 'formal',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 8
        },
        {
            'name': 'Windbreaker - Light',
            'description': 'Light windbreaker for moderate breezy days',
            'category': 'Outerwear',
            'price': 69.99,
            'activity_tag': 'outdoor',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 7
        },
        {
            'name': 'Yoga Leggings - Flexible',
            'description': 'Flexible yoga leggings for moderate temperatures',
            'category': 'Bottoms',
            'price': 44.99,
            'activity_tag': 'yoga',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 6
        },
        {
            'name': 'Casual Shirt - Office Ready',
            'description': 'Office-ready casual shirt for moderate weather',
            'category': 'Shirts',
            'price': 54.99,
            'activity_tag': 'business',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 7
        },
        {
            'name': 'Light Sweater - Comfort',
            'description': 'Comfortable light sweater for moderate weather',
            'category': 'Knitwear',
            'price': 64.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 6
        },
        {
            'name': 'Track Suit - Complete',
            'description': 'Complete track suit for moderate workouts',
            'category': 'Sports Wear',
            'price': 89.99,
            'activity_tag': 'gym',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 8
        },
        {
            'name': 'Casual Dress - Summer',
            'description': 'Summer casual dress for moderate weather',
            'category': 'Dresses',
            'price': 74.99,
            'activity_tag': 'casual',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 7
        },
        {
            'name': 'Cotton Cap - Sporty',
            'description': 'Sporty cotton cap for moderate weather',
            'category': 'Accessories',
            'price': 19.99,
            'activity_tag': 'sports',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 4
        },
        {
            'name': 'Light Jacket - Travel',
            'description': 'Light travel jacket for moderate climates',
            'category': 'Outerwear',
            'price': 94.99,
            'activity_tag': 'travel',
            'temp_category': 'moderate',
            'suitable_locations': 'bangalore, pune, hyderabad, delhi, mumbai',
            'priority_score': 8
        }
    ]
    
    created_count = 0
    for product_data in moderate_products:
        product = Product.objects.create(**product_data)
        created_count += 1
        print(f"Created moderate product: {product.name}")
    
    return created_count

def add_hot_products():
    """Add 20 hot temperature products"""
    hot_products = [
        {
            'name': 'Summer Shorts - Beach Ready',
            'description': 'Beach-ready summer shorts for hot weather',
            'category': 'Bottoms',
            'price': 24.99,
            'activity_tag': 'beach',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 7
        },
        {
            'name': 'Tank Top - Athletic',
            'description': 'Athletic tank top for hot weather workouts',
            'category': 'Tops',
            'price': 19.99,
            'activity_tag': 'gym',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 5
        },
        {
            'name': 'Linen Shorts - Casual',
            'description': 'Casual linen shorts for hot summer days',
            'category': 'Bottoms',
            'price': 34.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Cotton Vest - Sleeveless',
            'description': 'Sleeveless cotton vest for extreme heat',
            'category': 'Tops',
            'price': 16.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 4
        },
        {
            'name': 'Beach Shirt - Hawaiian',
            'description': 'Hawaiian style beach shirt for hot weather',
            'category': 'Shirts',
            'price': 39.99,
            'activity_tag': 'beach',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Sports Sandals - Outdoor',
            'description': 'Outdoor sports sandals for hot weather',
            'category': 'Footwear',
            'price': 44.99,
            'activity_tag': 'outdoor',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 7
        },
        {
            'name': 'Sun Hat - Wide Brim',
            'description': 'Wide brim sun hat for hot weather protection',
            'category': 'Accessories',
            'price': 24.99,
            'activity_tag': 'outdoor',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 5
        },
        {
            'name': 'Quick Dry T-Shirt - Hiking',
            'description': 'Quick dry t-shirt for hot weather hiking',
            'category': 'Tops',
            'price': 29.99,
            'activity_tag': 'hiking',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Summer Dress - Floral',
            'description': 'Floral summer dress for hot weather',
            'category': 'Dresses',
            'price': 54.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 7
        },
        {
            'name': 'Board Shorts - Surf',
            'description': 'Surf board shorts for beach activities',
            'category': 'Bottoms',
            'price': 39.99,
            'activity_tag': 'beach',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Cotton Cap - Baseball',
            'description': 'Baseball style cotton cap for sun protection',
            'category': 'Accessories',
            'price': 14.99,
            'activity_tag': 'sports',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 4
        },
        {
            'name': 'Linen Pants - Loose Fit',
            'description': 'Loose fit linen pants for hot weather comfort',
            'category': 'Bottoms',
            'price': 49.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Swim Trunks - Pool',
            'description': 'Pool swim trunks for hot weather swimming',
            'category': 'Swimwear',
            'price': 29.99,
            'activity_tag': 'swimming',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Sunglasses - UV Protection',
            'description': 'UV protection sunglasses for hot weather',
            'category': 'Accessories',
            'price': 34.99,
            'activity_tag': 'outdoor',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 5
        },
        {
            'name': 'Cooling Towel - Sport',
            'description': 'Sport cooling towel for hot weather activities',
            'category': 'Accessories',
            'price': 19.99,
            'activity_tag': 'sports',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 4
        },
        {
            'name': 'Summer Sandals - Comfort',
            'description': 'Comfortable summer sandals for hot weather',
            'category': 'Footwear',
            'price': 34.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Lightweight Shorts - Running',
            'description': 'Lightweight running shorts for hot weather',
            'category': 'Bottoms',
            'price': 26.99,
            'activity_tag': 'running',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 5
        },
        {
            'name': 'Beach Cover-Up - Stylish',
            'description': 'Stylish beach cover-up for hot weather',
            'category': 'Beachwear',
            'price': 44.99,
            'activity_tag': 'beach',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 6
        },
        {
            'name': 'Cotton Bandana - Multi',
            'description': 'Multi-purpose cotton bandana for hot weather',
            'category': 'Accessories',
            'price': 9.99,
            'activity_tag': 'outdoor',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 3
        },
        {
            'name': 'Summer Hat - Striped',
            'description': 'Striped summer hat for sun protection',
            'category': 'Accessories',
            'price': 22.99,
            'activity_tag': 'casual',
            'temp_category': 'hot',
            'suitable_locations': 'goa, mumbai, chennai, kerala, hyderabad',
            'priority_score': 5
        }
    ]
    
    created_count = 0
    for product_data in hot_products:
        product = Product.objects.create(**product_data)
        created_count += 1
        print(f"Created hot product: {product.name}")
    
    return created_count

if __name__ == "__main__":
    print("Adding moderate temperature products...")
    moderate_count = add_moderate_products()
    
    print(f"\nAdding hot temperature products...")
    hot_count = add_hot_products()
    
    print(f"\n✅ Successfully created {moderate_count} moderate and {hot_count} hot temperature products!")
    
    # Show current product counts
    total_products = Product.objects.count()
    cold_products = Product.objects.filter(temp_category='cold').count()
    moderate_products = Product.objects.filter(temp_category='moderate').count()
    hot_products = Product.objects.filter(temp_category='hot').count()
    
    print(f"\n📊 Current Product Database:")
    print(f"Total Products: {total_products}")
    print(f"Cold Products: {cold_products}")
    print(f"Moderate Products: {moderate_products}")
    print(f"Hot Products: {hot_products}")
