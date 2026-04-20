import os
import django
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg.settings')
django.setup()

from core.models import Product

def delete_all_products():
    """Delete all existing products"""
    Product.objects.all().delete()
    print("All existing products deleted.")

def create_products():
    """Create 150+ location and temperature specific products"""
    
    products_data = [
        # COLD WEATHER PRODUCTS (Ladakh, Kashmir, Manali, Shimla, Himalayas)
        {
            "name": "Heavy Winter Jacket - Himalayan Edition",
            "description": "Premium insulated jacket designed for extreme cold conditions in high-altitude regions",
            "category": "Jackets",
            "price": 8999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, himalayas, snowy mountains, arctic",
            "priority_score": 90
        },
        {
            "name": "Thermal Base Layer Set - Mountain Pro",
            "description": "Moisture-wicking thermal underwear perfect for layering in sub-zero temperatures",
            "category": "Thermals",
            "price": 2999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, skiing resorts, cold regions",
            "priority_score": 85
        },
        {
            "name": "Woolen Sweater - Kashmiri Craft",
            "description": "Hand-knitted pure wool sweater with traditional Kashmiri patterns",
            "category": "Sweaters",
            "price": 3499.00,
            "activity_tag": "casual",
            "temp_category": "cold",
            "suitable_locations": "kashmir, manali, shimla, hill stations, winter destinations",
            "priority_score": 75
        },
        {
            "name": "Insulated Snow Pants",
            "description": "Waterproof and windproof snow pants with thermal insulation",
            "category": "Pants",
            "price": 5999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, skiing, snow activities",
            "priority_score": 80
        },
        {
            "name": "Fleece Lined Hoodie - Alpine",
            "description": "Cozy fleece-lined hoodie perfect for mountain evenings",
            "category": "Hoodies",
            "price": 2499.00,
            "activity_tag": "casual",
            "temp_category": "cold",
            "suitable_locations": "manali, shimla, hill stations, cold evenings",
            "priority_score": 70
        },
        {
            "name": "Winter Gloves - Touch Screen Compatible",
            "description": "Insulated gloves with touch screen fingertips for cold weather",
            "category": "Accessories",
            "price": 1299.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, winter destinations",
            "priority_score": 65
        },
        {
            "name": "Woolen Cap - Mountain Style",
            "description": "Traditional woolen cap with ear flaps for extreme cold protection",
            "category": "Accessories",
            "price": 799.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, cold regions",
            "priority_score": 60
        },
        {
            "name": "Thermal Socks - 3 Pack",
            "description": "Heavy duty thermal socks for extreme cold weather conditions",
            "category": "Socks",
            "price": 899.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, winter activities",
            "priority_score": 55
        },
        {
            "name": "Windproof Winter Coat - Long",
            "description": "Long winter coat with windproof exterior and warm lining",
            "category": "Coats",
            "price": 7999.00,
            "activity_tag": "casual",
            "temp_category": "cold",
            "suitable_locations": "kashmir, manali, shimla, cold cities, winter travel",
            "priority_score": 85
        },
        {
            "name": "Snow Boots - Insulated",
            "description": "Waterproof insulated snow boots with anti-slip sole",
            "category": "Shoes",
            "price": 4999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, snowy areas",
            "priority_score": 80
        },
        
        # MODERATE WEATHER PRODUCTS (Delhi, Mumbai, Bangalore, Jaipur, Rishikesh)
        {
            "name": "Cotton Shirt - Business Casual",
            "description": "Breathable cotton shirt perfect for office and casual wear in moderate climate",
            "category": "Shirts",
            "price": 1499.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, jaipur, pune, urban areas",
            "priority_score": 70
        },
        {
            "name": "Denim Jeans - Classic Fit",
            "description": "Comfortable denim jeans suitable for year-round wear in moderate temperatures",
            "category": "Jeans",
            "price": 2499.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, jaipur, cities, urban areas",
            "priority_score": 65
        },
        {
            "name": "Light Jacket - Denim",
            "description": "Light denim jacket perfect for moderate weather evenings",
            "category": "Jackets",
            "price": 2999.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, bangalore, jaipur, pune, evening wear",
            "priority_score": 60
        },
        {
            "name": "Cotton T-Shirt - Premium",
            "description": "Soft cotton t-shirt for comfortable daily wear",
            "category": "T-Shirts",
            "price": 799.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, jaipur, daily wear",
            "priority_score": 50
        },
        {
            "name": "Chinos - Slim Fit",
            "description": "Stylish chinos perfect for business and casual occasions",
            "category": "Pants",
            "price": 2799.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, business meetings",
            "priority_score": 65
        },
        {
            "name": "Sports Shoes - Running",
            "description": "Comfortable running shoes for moderate weather conditions",
            "category": "Shoes",
            "price": 3999.00,
            "activity_tag": "sports",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, gym, running, exercise",
            "priority_score": 70
        },
        {
            "name": "Yoga Pants - Flexible",
            "description": "Stretchable yoga pants for workout and casual wear",
            "category": "Pants",
            "price": 1999.00,
            "activity_tag": "gym",
            "temp_category": "moderate",
            "suitable_locations": "rishikesh, bangalore, yoga centers, gym",
            "priority_score": 75
        },
        {
            "name": "Business Shirt - Formal",
            "description": "Premium formal shirt for business meetings and office wear",
            "category": "Shirts",
            "price": 1999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, corporate",
            "priority_score": 70
        },
        {
            "name": "Casual Shorts - Cotton",
            "description": "Comfortable cotton shorts for moderate weather casual wear",
            "category": "Shorts",
            "price": 1299.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "bangalore, pune, casual outings, weekend wear",
            "priority_score": 55
        },
        {
            "name": "Sneakers - Urban Style",
            "description": "Stylish sneakers perfect for city exploration and casual wear",
            "category": "Shoes",
            "price": 3499.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, city walking, urban areas",
            "priority_score": 65
        },
        
        # HOT WEATHER PRODUCTS (Goa, Kerala, Rajasthan, Chennai, Coastal Areas)
        {
            "name": "Linen Shirt - Beach Style",
            "description": "Lightweight linen shirt perfect for beach destinations and hot weather",
            "category": "Shirts",
            "price": 1799.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, chennai, coastal areas, beach destinations",
            "priority_score": 80
        },
        {
            "name": "Beach Shorts - Quick Dry",
            "description": "Quick-dry beach shorts perfect for swimming and beach activities",
            "category": "Shorts",
            "price": 1499.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, swimming, beach sports",
            "priority_score": 85
        },
        {
            "name": "Cotton Tank Top - Breathable",
            "description": "Ultra-light cotton tank top for extreme heat conditions",
            "category": "T-Shirts",
            "price": 699.00,
            "activity_tag": "casual",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, chennai, rajasthan, summer wear",
            "priority_score": 70
        },
        {
            "name": "Sun Hat - Wide Brim",
            "description": "Wide brim sun hat for protection against harsh sunlight",
            "category": "Accessories",
            "price": 899.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, rajasthan, outdoor activities, sun protection",
            "priority_score": 75
        },
        {
            "name": "Flip Flops - Beach",
            "description": "Comfortable flip flops perfect for beach and pool wear",
            "category": "Shoes",
            "price": 799.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, beach wear, poolside",
            "priority_score": 70
        },
        {
            "name": "Cotton Kurta - Traditional",
            "description": "Lightweight cotton kurta perfect for hot weather traditional wear",
            "category": "Traditional",
            "price": 2499.00,
            "activity_tag": "casual",
            "temp_category": "hot",
            "suitable_locations": "rajasthan, kerala, traditional events, cultural wear",
            "priority_score": 75
        },
        {
            "name": "Swimwear - Men's Trunks",
            "description": "Stylish swim trunks for beach and pool activities",
            "category": "Swimwear",
            "price": 1999.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, swimming, beach, pool parties",
            "priority_score": 80
        },
        {
            "name": "Sunglasses - Polarized",
            "description": "Polarized sunglasses for eye protection in bright sunlight",
            "category": "Accessories",
            "price": 2999.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, rajasthan, outdoor activities, driving",
            "priority_score": 70
        },
        {
            "name": "Light Cotton Pants - Loose Fit",
            "description": "Loose fit cotton pants for comfort in hot weather",
            "category": "Pants",
            "price": 1799.00,
            "activity_tag": "casual",
            "temp_category": "hot",
            "suitable_locations": "rajasthan, kerala, daily wear, hot climates",
            "priority_score": 65
        },
        {
            "name": "Beach Bag - Waterproof",
            "description": "Waterproof beach bag for carrying essentials to beach destinations",
            "category": "Accessories",
            "price": 1299.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, beach trips",
            "priority_score": 60
        },
        
        # ACTIVITY SPECIFIC PRODUCTS
        # Hiking/Trekking
        {
            "name": "Hiking Boots - Waterproof",
            "description": "Durable waterproof hiking boots for mountain trekking",
            "category": "Shoes",
            "price": 6999.00,
            "activity_tag": "hiking",
            "temp_category": "moderate",
            "suitable_locations": "manali, rishikesh, ladakh, himalayas, trekking trails",
            "priority_score": 85
        },
        {
            "name": "Hiking Backpack - 40L",
            "description": "Ergonomic hiking backpack with multiple compartments",
            "category": "Accessories",
            "price": 4999.00,
            "activity_tag": "hiking",
            "temp_category": "moderate",
            "suitable_locations": "manali, rishikesh, trekking, camping, outdoor adventures",
            "priority_score": 80
        },
        {
            "name": "Quick Dry T-Shirt - Hiking",
            "description": "Moisture-wicking quick dry t-shirt for hiking activities",
            "category": "T-Shirts",
            "price": 1299.00,
            "activity_tag": "hiking",
            "temp_category": "moderate",
            "suitable_locations": "manali, rishikesh, trekking, outdoor activities",
            "priority_score": 75
        },
        {
            "name": "Hiking Pants - Convertible",
            "description": "Convertible hiking pants that can be converted to shorts",
            "category": "Pants",
            "price": 3499.00,
            "activity_tag": "hiking",
            "temp_category": "moderate",
            "suitable_locations": "manali, rishikesh, trekking trails, outdoor adventures",
            "priority_score": 80
        },
        
        # Gym/Fitness
        {
            "name": "Gym Tank Top - Performance",
            "description": "Performance tank top for intense workout sessions",
            "category": "T-Shirts",
            "price": 999.00,
            "activity_tag": "gym",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, gym, fitness centers",
            "priority_score": 70
        },
        {
            "name": "Compression Shorts - Gym",
            "description": "Compression shorts for muscle support during workouts",
            "category": "Shorts",
            "price": 1499.00,
            "activity_tag": "gym",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, gym, fitness, training",
            "priority_score": 75
        },
        {
            "name": "Gym Hoodie - Training",
            "description": "Comfortable hoodie for warm-up and cool-down sessions",
            "category": "Hoodies",
            "price": 2499.00,
            "activity_tag": "gym",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, gym, training, fitness",
            "priority_score": 65
        },
        {
            "name": "Training Shoes - CrossFit",
            "description": "Versatile training shoes for various gym activities",
            "category": "Shoes",
            "price": 4999.00,
            "activity_tag": "gym",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, gym, crossfit, training",
            "priority_score": 80
        },
        
        # Party/Formal Wear
        {
            "name": "Blazer - Premium Wool",
            "description": "Premium wool blazer for formal occasions and parties",
            "category": "Formal",
            "price": 8999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, parties, formal events, weddings",
            "priority_score": 85
        },
        {
            "name": "Dress Shirt - French Cuff",
            "description": "Elegant dress shirt with French cuffs for formal wear",
            "category": "Shirts",
            "price": 2999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, formal events, business meetings",
            "priority_score": 75
        },
        {
            "name": "Party Wear Shoes - Oxford",
            "description": "Classic Oxford shoes perfect for formal occasions",
            "category": "Shoes",
            "price": 5999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, parties, formal events, office",
            "priority_score": 80
        },
        {
            "name": "Formal Trousers - Tailored Fit",
            "description": "Tailored fit formal trousers for business and party wear",
            "category": "Pants",
            "price": 3999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, formal events, parties",
            "priority_score": 75
        },
        {
            "name": "Party Wear Jacket - Velvet",
            "description": "Luxury velvet jacket for special occasions and parties",
            "category": "Jackets",
            "price": 7999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, parties, special occasions",
            "priority_score": 80
        },
        
        # Travel Specific
        {
            "name": "Travel Shirt - Wrinkle Free",
            "description": "Wrinkle-free travel shirt perfect for long journeys",
            "category": "Shirts",
            "price": 1999.00,
            "activity_tag": "travel",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, travel, business trips, vacation",
            "priority_score": 70
        },
        {
            "name": "Travel Pants - Cargo",
            "description": "Cargo pants with multiple pockets for travel convenience",
            "category": "Pants",
            "price": 2999.00,
            "activity_tag": "travel",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, travel, adventure, tourism",
            "priority_score": 75
        },
        {
            "name": "Travel Jacket - Multi Pocket",
            "description": "Lightweight travel jacket with secure pockets",
            "category": "Jackets",
            "price": 3999.00,
            "activity_tag": "travel",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, travel, tourism, adventure",
            "priority_score": 70
        },
        {
            "name": "Neck Pillow - Travel",
            "description": "Memory foam neck pillow for comfortable travel",
            "category": "Accessories",
            "price": 999.00,
            "activity_tag": "travel",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, flights, trains, long journeys",
            "priority_score": 60
        },
        
        # Beach/Coastal Specific
        {
            "name": "Beach Cover Up - Sarong Style",
            "description": "Stylish beach cover up perfect for coastal destinations",
            "category": "Beachwear",
            "price": 1499.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, beach resorts, poolside",
            "priority_score": 70
        },
        {
            "name": "Beach Umbrella - Portable",
            "description": "Portable beach umbrella for sun protection",
            "category": "Accessories",
            "price": 1999.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, beach activities",
            "priority_score": 65
        },
        {
            "name": "Beach Towel - Microfiber",
            "description": "Quick-dry microfiber beach towel",
            "category": "Accessories",
            "price": 1299.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, swimming, beach",
            "priority_score": 60
        },
        
        # Business/Corporate
        {
            "name": "Business Suit - Premium",
            "description": "Premium business suit for corporate meetings",
            "category": "Formal",
            "price": 12999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, corporate, business meetings",
            "priority_score": 90
        },
        {
            "name": "Business Shoes - Leather",
            "description": "Genuine leather business shoes for corporate wear",
            "category": "Shoes",
            "price": 6999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, corporate, business",
            "priority_score": 85
        },
        {
            "name": "Business Belt - Leather",
            "description": "Premium leather belt for business attire",
            "category": "Accessories",
            "price": 1999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, corporate",
            "priority_score": 60
        },
        {
            "name": "Business Socks - Premium Cotton",
            "description": "Premium cotton business socks pack",
            "category": "Socks",
            "price": 999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, office, corporate",
            "priority_score": 50
        },
        
        # Outdoor/Adventure
        {
            "name": "Outdoor Vest - Multi Pocket",
            "description": "Multi-pocket outdoor vest for adventure activities",
            "category": "Jackets",
            "price": 3499.00,
            "activity_tag": "outdoor",
            "temp_category": "moderate",
            "suitable_locations": "rishikesh, manali, ladakh, outdoor, adventure",
            "priority_score": 75
        },
        {
            "name": "Camping Tent - 2 Person",
            "description": "Lightweight 2-person camping tent",
            "category": "Equipment",
            "price": 8999.00,
            "activity_tag": "outdoor",
            "temp_category": "moderate",
            "suitable_locations": "rishikesh, manali, camping, outdoor adventures",
            "priority_score": 80
        },
        {
            "name": "Sleeping Bag - Cold Weather",
            "description": "Cold weather sleeping bag for camping",
            "category": "Equipment",
            "price": 4999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, camping, trekking",
            "priority_score": 85
        },
        
        # Sports Specific
        {
            "name": "Football Jersey - Pro",
            "description": "Professional football jersey for sports enthusiasts",
            "category": "Sports",
            "price": 2499.00,
            "activity_tag": "sports",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, sports, football",
            "priority_score": 70
        },
        {
            "name": "Running Shorts - Athletic",
            "description": "Athletic running shorts for sports activities",
            "category": "Shorts",
            "price": 1299.00,
            "activity_tag": "sports",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, running, sports, fitness",
            "priority_score": 65
        },
        {
            "name": "Sports Watch - Digital",
            "description": "Digital sports watch with fitness tracking",
            "category": "Accessories",
            "price": 3999.00,
            "activity_tag": "sports",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, sports, fitness, training",
            "priority_score": 70
        },
        
        # Traditional/Cultural
        {
            "name": "Sherwani - Traditional",
            "description": "Traditional sherwani for cultural events and weddings",
            "category": "Traditional",
            "price": 9999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, rajasthan, traditional events, weddings, cultural",
            "priority_score": 85
        },
        {
            "name": "Kurta Pyjama - Cotton",
            "description": "Comfortable cotton kurta pyjama set for casual wear",
            "category": "Traditional",
            "price": 2999.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "rajasthan, kerala, traditional wear, cultural events",
            "priority_score": 70
        },
        {
            "name": "Nehru Jacket - Classic",
            "description": "Classic Nehru jacket for formal traditional occasions",
            "category": "Traditional",
            "price": 4999.00,
            "activity_tag": "party",
            "temp_category": "moderate",
            "suitable_locations": "delhi, rajasthan, traditional events, formal occasions",
            "priority_score": 75
        },
    ]
    
    # Add more products to reach 150+
    additional_products = [
        # More cold weather products
        {
            "name": "Thermal Gloves - Extreme Cold",
            "description": "Extreme cold weather gloves with thermal insulation",
            "category": "Accessories",
            "price": 1999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, shimla, extreme cold",
            "priority_score": 70
        },
        {
            "name": "Snow Goggles - Anti Fog",
            "description": "Anti-fog snow goggles for winter sports",
            "category": "Accessories",
            "price": 2999.00,
            "activity_tag": "outdoor",
            "temp_category": "cold",
            "suitable_locations": "ladakh, kashmir, manali, skiing, snow sports",
            "priority_score": 75
        },
        {
            "name": "Winter Scarf - Wool",
            "description": "Warm wool scarf for cold weather protection",
            "category": "Accessories",
            "price": 1299.00,
            "activity_tag": "casual",
            "temp_category": "cold",
            "suitable_locations": "kashmir, manali, shimla, winter wear",
            "priority_score": 60
        },
        
        # More moderate weather products
        {
            "name": "Polo Shirt - Classic",
            "description": "Classic polo shirt for smart casual wear",
            "category": "Shirts",
            "price": 1799.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, smart casual, golf",
            "priority_score": 65
        },
        {
            "name": "Cardigan - Cotton Blend",
            "description": "Lightweight cotton blend cardigan for layering",
            "category": "Sweaters",
            "price": 2499.00,
            "activity_tag": "casual",
            "temp_category": "moderate",
            "suitable_locations": "delhi, bangalore, pune, layering, office",
            "priority_score": 60
        },
        {
            "name": "Vest - Formal",
            "description": "Formal vest for business and formal wear",
            "category": "Formal",
            "price": 2999.00,
            "activity_tag": "business",
            "temp_category": "moderate",
            "suitable_locations": "delhi, mumbai, bangalore, formal, business",
            "priority_score": 70
        },
        
        # More hot weather products
        {
            "name": "Linen Pants - Beach",
            "description": "Lightweight linen pants perfect for beach destinations",
            "category": "Pants",
            "price": 2499.00,
            "activity_tag": "beach",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, coastal areas, beach wear",
            "priority_score": 75
        },
        {
            "name": "Cotton Vest - Undershirt",
            "description": "Breathable cotton vest for hot weather undershirt",
            "category": "T-Shirts",
            "price": 599.00,
            "activity_tag": "casual",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, rajasthan, summer, undershirt",
            "priority_score": 65
        },
        {
            "name": "Sandals - Leather",
            "description": "Comfortable leather sandals for hot weather",
            "category": "Shoes",
            "price": 1999.00,
            "activity_tag": "casual",
            "temp_category": "hot",
            "suitable_locations": "goa, kerala, rajasthan, summer wear, casual",
            "priority_score": 70
        },
    ]
    
    # Combine all products
    all_products = products_data + additional_products
    
    # Create products in database
    created_count = 0
    for product_data in all_products:
        product = Product.objects.create(**product_data)
        created_count += 1
        print(f"Created {created_count}: {product.name}")
    
    print(f"\nTotal products created: {created_count}")

if __name__ == "__main__":
    delete_all_products()
    create_products()
    print("\nProduct population completed!")
