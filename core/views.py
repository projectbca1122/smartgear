import json
import speech_recognition as sr
import pyttsx3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, F, Q
from django.utils import timezone
from google.generativeai import configure, GenerativeModel
from .models import Product, User, Cart, CartItem, OTP, Order, OrderItem, Wishlist
import random
import hashlib
import requests
import re
from datetime import timedelta, datetime

# Configure Gemini API
API_KEY = "AIzaSyBAL6xjruJ20Qn7unR-Kjo2GocqL8LonzU"
configure(api_key=API_KEY)
model = GenerativeModel("gemini-2.5-flash")

# Weather API configuration
WEATHER_API_KEY = "e0f58f02ae07966898ecf53c37dca217"  # You'll need to get this from OpenWeatherMap
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Initialize text-to-speech engine
engine = pyttsx3.init()

def get_weather_info(location):
    """Get weather information for a location using OpenWeatherMap API - enhanced for any city/country"""
    try:
        # Map common locations to coordinates for better accuracy
        location_coords = {
            # Indian locations
            'manali': {'lat': 32.2396, 'lon': 77.1888},
            'goa': {'lat': 15.2993, 'lon': 74.1240},
            'delhi': {'lat': 28.6139, 'lon': 77.2090},
            'mumbai': {'lat': 19.0760, 'lon': 72.8777},
            'bangalore': {'lat': 12.9716, 'lon': 77.5946},
            'shimla': {'lat': 31.1048, 'lon': 77.1734},
            'rishikesh': {'lat': 30.0869, 'lon': 78.2676},
            'jaipur': {'lat': 26.9124, 'lon': 75.7873},
            'kashmir': {'lat': 34.0837, 'lon': 74.7973},
            'ladakh': {'lat': 34.1526, 'lon': 77.5771},
            # African destinations
            'africa': {'lat': -8.7832, 'lon': 34.5085},  # Central Africa
            'kenya': {'lat': -0.0236, 'lon': 37.9062},
            'nairobi': {'lat': -1.2921, 'lon': 36.8219},
            'south africa': {'lat': -30.5595, 'lon': 22.9375},
            'cape town': {'lat': -33.9249, 'lon': 18.4241},
            'johannesburg': {'lat': -26.2041, 'lon': 28.0473},
            'egypt': {'lat': 26.8206, 'lon': 30.8025},
            'cairo': {'lat': 30.0444, 'lon': 31.2357},
            'morocco': {'lat': 31.7917, 'lon': -7.0926},
            'marrakech': {'lat': 31.6295, 'lon': -7.9811},
            'tanzania': {'lat': -6.3690, 'lon': 34.8888},
            'kilimanjaro': {'lat': -3.0674, 'lon': 37.3556},
            # International destinations
            'dubai': {'lat': 25.2048, 'lon': 55.2708},
            'singapore': {'lat': 1.3521, 'lon': 103.8198},
            'thailand': {'lat': 15.8700, 'lon': 100.9925},
            'bangkok': {'lat': 13.7563, 'lon': 100.5018},
            'malaysia': {'lat': 4.2105, 'lon': 101.9758},
            'kuala lumpur': {'lat': 3.1390, 'lon': 101.6869},
            'usa': {'lat': 39.8283, 'lon': -98.5795},
            'new york': {'lat': 40.7128, 'lon': -74.0060},
            'london': {'lat': 51.5074, 'lon': -0.1278},
            'paris': {'lat': 48.8566, 'lon': 2.3522},
            'tokyo': {'lat': 35.6762, 'lon': 139.6503},
            'sydney': {'lat': -33.8688, 'lon': 151.2093}
        }
        
        location_lower = location.lower().strip()
        
        # Use coordinates if available for known locations
        if location_lower in location_coords:
            coords = location_coords[location_lower]
            url = f"{WEATHER_BASE_URL}?lat={coords['lat']}&lon={coords['lon']}&appid={WEATHER_API_KEY}&units=metric"
        else:
            # Use location name for any other city/country - this works for ANY location!
            # Format the location properly for the API
            formatted_location = location.title() if ' ' in location else location.capitalize()
            url = f"{WEATHER_BASE_URL}?q={formatted_location}&appid={WEATHER_API_KEY}&units=metric"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'location': data['name'],
                'success': True
            }
            return weather_info
        else:
            # Try alternative approach: add country code for better accuracy
            if ',' not in location:  # If no country specified
                common_countries = {
                    'paris': 'Paris,FR',
                    'london': 'London,GB',
                    'berlin': 'Berlin,DE',
                    'rome': 'Rome,IT',
                    'madrid': 'Madrid,ES',
                    'amsterdam': 'Amsterdam,NL',
                    'tokyo': 'Tokyo,JP',
                    'beijing': 'Beijing,CN',
                    'moscow': 'Moscow,RU',
                    'dubai': 'Dubai,AE'
                }
                
                if location_lower in common_countries:
                    url = f"{WEATHER_BASE_URL}?q={common_countries[location_lower]}&appid={WEATHER_API_KEY}&units=metric"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        weather_info = {
                            'temperature': data['main']['temp'],
                            'feels_like': data['main']['feels_like'],
                            'humidity': data['main']['humidity'],
                            'description': data['weather'][0]['description'],
                            'location': data['name'],
                            'success': True
                        }
                        return weather_info
            
            return {'success': False, 'error': f'Weather data not available for {location}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_location_from_message(message):
    """Extract location names from user message - enhanced to handle any city/country"""
    message_lower = message.lower()
    
    # Common travel indicators to identify location context
    travel_indicators = ['going to', 'visiting', 'traveling to', 'trip to', 'going for', 'planning to', 'heading to', 'moving to', 'going', 'going on a tour to', 'tour to', 'on a tour to']
    
    # Check if this is a travel query
    is_travel_query = any(indicator in message_lower for indicator in travel_indicators)
    
    if not is_travel_query:
        return None
    
    # Enhanced location extraction using patterns
    import re
    
    # Pattern 1: "going to [location]" or similar patterns
    for indicator in travel_indicators:
        pattern = re.compile(re.escape(indicator) + r'\s+([a-zA-Z\s]+)', re.IGNORECASE)
        match = pattern.search(message)
        if match:
            location = match.group(1).strip()
            # Clean up the location (remove trailing words like 'next week', 'for vacation', etc.)
            location = re.sub(r'\b(next week|for vacation|for holiday|in summer|in winter|tomorrow|today|next month)\b.*$', '', location).strip()
            if location and len(location) > 1:
                return [location.lower()]
    
    # Pattern 2: Look for common location indicators
    location_patterns = [
        r'\b(in|at|from)\s+([A-Z][a-zA-Z\s]{2,})\b',  # "in Mumbai", "from Delhi"
        r'\b([A-Z][a-z]+\s*,\s*[A-Z][a-z]+)\b',  # "Paris, France"
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'  # "New York", "South Africa"
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, message)
        for match in matches:
            if isinstance(match, tuple):
                location = match[1] if len(match) > 1 else match[0]
            else:
                location = match
            location = location.strip()
            if location and len(location) > 2:
                return [location.lower()]
    
    # Pattern 3: Fallback - look for capitalized words that might be locations
    words = message.split()
    potential_locations = []
    
    for i, word in enumerate(words):
        # Check if word starts with capital letter and is not a common word
        if word[0].isupper() and word.lower() not in ['i', 'going', 'am', 'to', 'for', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'from', 'with', 'my']:
            # Check next few words to capture multi-word locations
            location_words = [word]
            j = i + 1
            while j < len(words) and j < i + 4:  # Max 4 words for location
                next_word = words[j]
                if next_word[0].isupper() or next_word.lower() in ['of', 'de', 'la', 'el', 'san', 'new', 'south', 'north', 'east', 'west']:
                    location_words.append(next_word)
                    j += 1
                else:
                    break
            
            location = ' '.join(location_words)
            # Filter out common non-location phrases
            if not any(phrase in location.lower() for phrase in ['next week', 'next month', 'this year', 'last year', 'good morning', 'good evening']):
                potential_locations.append(location.lower())
    
    return potential_locations[:1] if potential_locations else None

def get_weather_based_products(weather_info, user_message):
    """Get product recommendations based on weather conditions"""
    temp = weather_info['temperature']
    description = weather_info['description'].lower()
    location = weather_info.get('location', '').lower()
    
    # Base query for weather-appropriate products
    weather_conditions = []
    
    # Temperature-based recommendations
    if temp < 10:
        weather_conditions.extend(['warm', 'winter', 'fleece', 'jacket', 'sweater', 'insulated'])
    elif temp < 20:
        weather_conditions.extend(['light jacket', 'sweater', 'long sleeve', 'layered'])
    elif temp < 30:
        weather_conditions.extend(['comfortable', 'breathable', 'cotton', 'lightweight'])
    else:
        weather_conditions.extend(['summer', 'lightweight', 'breathable', 'shorts', 'linen', 'moisture wicking'])
    
    # Weather description-based recommendations
    if 'rain' in description or 'drizzle' in description or 'shower' in description:
        weather_conditions.extend(['waterproof', 'rain', 'quick dry', 'water resistant'])
    elif 'snow' in description:
        weather_conditions.extend(['waterproof', 'insulated', 'snow', 'winter', 'thermal'])
    elif 'clear' in description or 'sunny' in description:
        weather_conditions.extend(['uv protection', 'sun', 'hat', 'sunglasses', 'light colored'])
    elif 'cloud' in description or 'overcast' in description:
        weather_conditions.extend(['comfortable', 'versatile', 'all weather'])
    elif 'hot' in description or temp > 35:
        weather_conditions.extend(['cooling', 'ventilated', 'safari', 'sun protection'])
    
    # Location-specific recommendations
    if 'africa' in location or any(african_loc in location for african_loc in ['kenya', 'nairobi', 'tanzania', 'kilimanjaro']):
        weather_conditions.extend(['safari', 'adventure', 'outdoor', 'durable', 'neutral colors', 'insect resistant'])
    elif 'egypt' in location or 'cairo' in location or 'morocco' in location or 'marrakech' in location:
        weather_conditions.extend(['desert', 'breathable', 'loose fitting', 'sun protection', 'cultural'])
    elif 'south africa' in location or 'cape town' in location or 'johannesburg' in location:
        weather_conditions.extend(['versatile', 'all season', 'outdoor', 'casual elegant'])
    
    # Also extract activity keywords from user message
    activity_keywords = []
    activities = [
        'hiking', 'trekking', 'running', 'gym', 'workout', 'casual', 'formal', 
        'party', 'beach', 'travel', 'safari', 'adventure', 'desert', 'mountain',
        'wildlife', 'photography', 'camping', 'city tour', 'business'
    ]
    message_lower = user_message.lower()
    
    for activity in activities:
        if activity in message_lower:
            activity_keywords.append(activity)
    
    # Build product query
    products = Product.objects.all()
    relevant_products = []
    
    for product in products:
        product_text = f"{product.name.lower()} {product.description.lower()} {product.suitable_locations.lower()}"
        score = 0
        
        # Weather condition matching
        for condition in weather_conditions:
            if condition in product_text:
                score += 2
        
        # Activity matching
        for activity in activity_keywords:
            if activity in product_text:
                score += 3
        
        # Location matching
        locations = extract_location_from_message(user_message)
        if locations:
            for location in locations:
                if location in product_text:
                    score += 4
        
        # Africa-specific matching
        if 'africa' in message_lower:
            africa_keywords = ['safari', 'adventure', 'outdoor', 'travel', 'durable', 'neutral']
            for keyword in africa_keywords:
                if keyword in product_text:
                    score += 3
        
        if score > 0:
            relevant_products.append((product, score))
    
    # Sort by score and return top products
    relevant_products.sort(key=lambda x: x[1], reverse=True)
    return [product for product, score in relevant_products[:8]]

@csrf_exempt
@require_http_methods(["POST"])
def voice_assistant(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Get AI response
        ai_response = get_ai_response(user_message)
        
        # Use the same product logic as AI response for consistency
        products = get_consistent_products(user_message)
        
        response_data = {
            'ai_response': ai_response,
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category': product.category,
                    'price': str(product.price),
                    'image_url': product.image_url
                }
                for product in products
            ]
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_consistent_products(user_message):
    """Get products using the same logic as AI response for consistency"""
    user_message_lower = user_message.lower().strip()
    
    # Enhanced location and weather detection
    locations = extract_location_from_message(user_message)
    
    # Travel/going indicators
    travel_indicators = ['going to', 'visiting', 'traveling to', 'trip to', 'going for', 'planning to', 'heading to', 'moving to']
    # Also handle direct location requests
    location_request_indicators = ['products for', 'suggest me', 'show me', 'recommend', 'what to wear', 'what should i wear', 'gear for']
    
    is_travel_query = any(indicator in user_message_lower for indicator in travel_indicators)
    is_location_request = any(indicator in user_message_lower for indicator in location_request_indicators)
    
    # Check if this is a location-based request (either travel or direct location request)
    if locations and (is_travel_query or is_location_request):
        # Get weather for mentioned location
        location = locations[0]  # Use first mentioned location
        weather_info = get_weather_info(location)
        
        if weather_info['success']:
            # Get weather-based product recommendations
            weather_products = get_weather_based_products(weather_info, user_message)
            if weather_products:
                return weather_products[:8]  # Return same number as AI response
    
    # Fallback to regular product search
    return find_relevant_products(user_message)[:8]

def get_ai_response(user_message):
    try:
        user_message_lower = user_message.lower().strip()
        
        # Handle greetings with AI-generated responses
        greetings = ['hey', 'hello', 'hi there','good morning', 'good afternoon', 'good evening']
        if any(greeting in user_message_lower for greeting in greetings):
            try:
                # Use Gemini to generate contextual greeting response
                gemini_response = model.generate_content(f"Generate a friendly, personalized greeting response for SmartGear AI assistant. The user said: '{user_message}'. Keep it brief and mention that I can help with weather-based product recommendations.")
                return gemini_response.text
            except:
                # Fallback to static responses if AI fails
                responses = [
                    "Hello! I'm your SmartGear assistant. I can help you find perfect products based on weather and location! Just tell me where you're going.",
                    "Hi there! I'm your smart shopping assistant. I can check weather conditions and suggest the perfect gear for your trip!",
                    "Hey! Welcome to SmartGear. Tell me about your travel plans and I'll recommend the best products for the weather!"
                ]
                import random
                return random.choice(responses)
        
        # Handle navigation commands
        navigation_commands = {
            'profile': "I can help you navigate to your profile! Click on your name in the top right corner, then select 'Profile' from the dropdown menu. There you can view your personal information and order history.",
            'logout': "To logout, click on your name in the top right corner and select 'Logout' from the dropdown menu. This will securely sign you out of your account.",
            'orders': "You can check your orders by going to your profile and selecting 'My Orders'. There you'll see all your past and current orders with their status. Would you like me to help you find something specific?",
            'cart': "Your cart shows all items you've added. Click the shopping cart icon in the top right corner to view and manage your cart items. You can adjust quantities or remove items there.",
            'wishlist': "Your wishlist contains items you've saved for later. Access it through your profile menu. You can move items from wishlist to cart or purchase them directly!",
            'home': "You're already on the home page! Here you can browse our featured products and use the voice assistant to find exactly what you need.",
            'checkout': "Ready to checkout? Go to your cart and click the checkout button. You'll be guided through the payment process. Make sure your shipping details are up to date!",
            'account': "To manage your account, click on your name in the top right corner. From there you can access your profile, orders, wishlist, and account settings.",
            'signin': "To sign in, click the 'Sign In' button in the top right corner. You can sign in with your password or request an OTP sent to your email. If you're new, you can also create an account!",
            'sign in': "To sign in, click the 'Sign In' button in the top right corner. You can sign in with your password or request an OTP sent to your email. If you're new, you can also create an account!",
            'login': "To sign in, click the 'Sign In' button in the top right corner. You can sign in with your password or request an OTP sent to your email. If you're new, you can also create an account!",
            'help': "I'm here to help! You can ask me about products, navigation, or say things like 'show me hiking shoes' or 'take me to my profile'. I can also check weather and suggest products based on your destination!",
            'customer care':"Sure, You can contact them on this mobile number:+91 123456789 or Email: projectbca1122@gmail.com",
            'customer care number':"Sure, You can contact them on this mobile number:+91 123456789 or Email: projectbca1122@gmail.com"
        }
        
        # Check for navigation commands
        for command, response in navigation_commands.items():
            if command in user_message_lower:
                return response
        
        # Handle help requests with AI-generated responses
        help_keywords = ['help', 'how to', 'how do i', 'what can you do', 'assist']
        if any(keyword in user_message_lower for keyword in help_keywords):
            try:
                gemini_response = model.generate_content(f"Generate a helpful, personalized response about SmartGear AI assistant capabilities. The user asked: '{user_message}'. Explain weather intelligence, product recommendations, and navigation features in a conversational way.")
                return gemini_response.text
            except:
                return """I'm your SmartGear AI assistant with weather intelligence! Here's what I can help you with:

🌤️ **Weather-Based Recommendations**: Tell me your destination and I'll check the weather!
🛍️ **Smart Product Search**: Say "I'm going to Manali" or "beach trip to Goa"
🧭 **Navigation**: Say "take me to profile" or "show my orders"
💬 **Context-Aware Help**: I understand locations, activities, and weather conditions
🎯 **Precise Matching**: I find products perfect for your specific destination and weather

Just say where you're going and what you plan to do!"""
        
        # Handle common questions
        if 'who are you' in user_message_lower or 'what are you' in user_message_lower:
            return "I'm SmartGear's advanced AI assistant with weather intelligence! I can check real-time weather conditions for any destination and recommend the perfect products based on temperature, conditions, and your planned activities."
        
        if 'thank' in user_message_lower:
            return "You're very welcome! Is there anything else I can help you with today? I can check weather for more destinations or help with product recommendations!"
        
        if 'bye' in user_message_lower or 'goodbye' in user_message_lower:
            return "Goodbye! Thanks for visiting SmartGear. Have a wonderful trip with your perfect gear!"
        
        # Enhanced location and weather detection
        locations = extract_location_from_message(user_message)
        
        # Travel/going indicators
        travel_indicators = ['going to', 'visiting', 'traveling to', 'trip to', 'going for', 'planning to', 'heading to', 'moving to', 'going on a tour to', 'tour to', 'on a tour to']
        # Also handle direct location requests
        location_request_indicators = ['products for', 'suggest me', 'show me', 'recommend', 'what to wear', 'what should i wear', 'gear for']
        
        is_travel_query = any(indicator in user_message_lower for indicator in travel_indicators)
        is_location_request = any(indicator in user_message_lower for indicator in location_request_indicators)
        
        # Check if this is a location-based request (either travel or direct location request)
        if locations and (is_travel_query or is_location_request):
            # Get weather for the mentioned location
            location = locations[0]  # Use first mentioned location
            weather_info = get_weather_info(location)
            
            if weather_info['success']:
                # Get weather-based product recommendations
                weather_products = get_weather_based_products(weather_info, user_message)
                
                response = f"Weather Update for {weather_info['location'].title()}:\n"
                response += f"Temperature: {weather_info['temperature']:.1f}°C\n\n"
                
                response += f"Recommended Products for {location.title()}:\n\n"
                
                if weather_products:
                    for i, product in enumerate(weather_products[:6], 1):
                        response += f"{i}. {product.name}\n"
                    
                    if len(weather_products) > 6:
                        response += f"And {len(weather_products) - 6} more products available."
                else:
                    response += "I'm checking for the best products for these weather conditions. Let me find some alternatives for you."
                    # Fallback to regular search
                    fallback_products = find_relevant_products(user_message)
                    if fallback_products:
                        response += "\n\nHere are some alternatives:\n\n"
                        for i, product in enumerate(fallback_products[:4], 1):
                            response += f"{i}. {product.name}\n"
                
                return response
            else:
                # Weather API failed, but we still have location
                response = f"Here are some great products for your needs:\n\n"
                
                location_products = find_relevant_products(user_message)
                if location_products:
                    for i, product in enumerate(location_products[:5], 1):
                        response += f"{i}. {product.name}\n"
                else:
                    response += "Let me help you find products. Try mentioning specific activities like 'hiking', 'beach', or 'casual'."
                
                return response
                
                response = f"Weather Update for {weather_info['location'].title()}:\n"
                response += f"Temperature: {weather_info['temperature']:.1f}°C\n\n"
                
                response += f"Recommended Products for {location.title()}:\n\n"
                
                if weather_products:
                    for i, product in enumerate(weather_products[:6], 1):
                        response += f"{i}. {product.name}\n"
                    
                    if len(weather_products) > 6:
                        response += f"And {len(weather_products) - 6} more products available."
                else:
                    response += "I'm checking for the best products for these weather conditions. Let me find some alternatives for you."
                    # Fallback to regular search
                    fallback_products = find_relevant_products(user_message)
                    if fallback_products:
                        response += "\n\nHere are some alternatives:\n\n"
                        for i, product in enumerate(fallback_products[:4], 1):
                            response += f"{i}. {product.name}\n"
                
                return response
        
        # Regular product search with enhanced matching
        relevant_products = find_relevant_products(user_message)
        
        if relevant_products:
            response = "Here are some recommend products:\n\n"
            for i, product in enumerate(relevant_products[:5], 1):
                response += f"{i}. {product.name}\n"
            
            if len(relevant_products) > 5:
                response += f"And {len(relevant_products) - 5} more products available."
            
            return response
        else:
            return """I couldn't find specific products matching your request. Here are some suggestions:

🌍 **Try with destinations**: 
- "I'm going to Manali" or "Beach trip to Goa"
- "Hiking in the mountains" or "City tour in Delhi"

🔍 **Try different keywords**: 
- For activities: "hiking", "beach", "gym", "office", "party"
- For product types: "shoes", "shirt", "jacket", "pants"

🗣️ **Ask me for help**: Say "help" to see all available commands
🧭 **Navigate**: Say "take me to profile" or "show my cart"

💡 **Smart Feature**: Tell me your destination and I'll check real-time weather to suggest perfect products!

What specifically are you looking for today?"""
    
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Please try again or type 'help' for assistance."

def find_relevant_products(user_message):
    """Enhanced product finding with better scoring and matching"""
    user_message_lower = user_message.lower()
    
    # Extract keywords with better categorization
    locations = extract_location_from_message(user_message) or []
    activities = ['hiking', 'trekking', 'swimming', 'workout', 'running', 'camping', 'travel', 'formal', 'informal', 'beach', 'gym', 'office', 'party', 'casual', 'business', 'mountain', 'city']
    product_types = ['shoes', 'shirt', 'pants', 'jacket', 'dress', 'shorts', 'top', 'sweater', 't-shirt', 'jeans', 'trousers', 'coat', 'hoodie', 'sports wear', 'ethnic wear']
    
    # Find mentioned activities and product types
    mentioned_activities = [activity for activity in activities if activity in user_message_lower]
    mentioned_product_types = [ptype for ptype in product_types if ptype in user_message_lower]
    
    # Get all products and score them
    products = Product.objects.all()
    scored_products = []
    
    for product in products:
        score = 0
        product_text = f"{product.name.lower()} {product.description.lower()} {product.suitable_locations.lower()}"
        
        # Exact product name matching (highest score)
        product_name_words = product.name.lower().split()
        user_words = user_message_lower.split()
        
        for user_word in user_words:
            for product_word in product_name_words:
                if user_word == product_word:
                    score += 10  # High score for exact word matches
        
        # Full product name match
        if product.name.lower() in user_message_lower:
            score += 15
        
        # Location matching (very high score)
        for location in locations:
            if location in product_text:
                score += 12
        
        # Activity matching (high score)
        for activity in mentioned_activities:
            if activity in product_text:
                score += 8
        
        # Product type matching (medium score)
        for ptype in mentioned_product_types:
            if ptype in product_text:
                score += 6
        
        # Category matching
        if product.category.lower() in user_message_lower:
            score += 5
        
        # Suitable locations matching
        for location in locations:
            if location in product.suitable_locations.lower():
                score += 7
        
        # Add to scored list if has any score
        if score > 0:
            scored_products.append((product, score))
    
    # Sort by score (highest first) and return top products
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # If no scored products, return some general recommendations
    if not scored_products:
        return list(products[:8])
    
    return [product for product, score in scored_products[:10]]

def home(request):
    return render(request, 'core/home.html')

@csrf_exempt
@require_http_methods(["POST"])
def text_to_speech(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        
        # Convert text to speech
        engine.say(text)
        engine.runAndWait()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_products(request):
    try:
        products = Product.objects.all()
        products_data = []
        
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'price': str(product.price),
                'image_url': product.image_url,
                'suitable_locations': product.suitable_locations
            })
        
        return JsonResponse(products_data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "projectbca1122@gmail.com"
SMTP_PASSWORD = "rwpt xrqa defc chna"

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def generate_otp():
    return str(random.randint(100000, 999999))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@csrf_exempt
@require_http_methods(["POST"])
def check_user_exists(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        # Check if user already exists
        user_exists = User.objects.filter(email=email).exists()
        
        return JsonResponse({
            'exists': user_exists,
            'message': 'User already exists' if user_exists else 'Email available'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to database
        OTP.objects.filter(email=email).delete()
        OTP.objects.create(email=email, otp=otp)
        
        # Send email
        subject = "StyleAI Assistant - Verify Your Email"
        body = f"""
        <h2>Email Verification</h2>
        <p>Your OTP for StyleAI Assistant is: <strong>{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        if send_email(email, subject, body):
            return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
        else:
            return JsonResponse({'error': 'Failed to send OTP'}, status=500)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_and_signup(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        name = data.get('name')
        gender = data.get('gender')
        password = data.get('password')
        
        if not all([email, otp, name, gender, password]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        # Verify OTP
        otp_obj = OTP.objects.filter(email=email, otp=otp, is_used=False).first()
        if not otp_obj:
            return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)
        
        # Check if OTP is expired (10 minutes)
        if timezone.now() - otp_obj.created_at > timedelta(minutes=10):
            return JsonResponse({'error': 'OTP expired'}, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User already exists'}, status=400)
        
        # Create user
        user = User.objects.create(
            name=name,
            email=email,
            gender=gender,
            password=hash_password(password),
            is_verified=True
        )
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'gender': user.gender
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def signin_with_password(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        if user.password != hash_password(password):
            return JsonResponse({'error': 'Invalid password'}, status=401)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'gender': user.gender
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_signin_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to database
        OTP.objects.filter(email=email).delete()
        OTP.objects.create(email=email, otp=otp)
        
        # Send email
        subject = "StyleAI Assistant - Sign In OTP"
        body = f"""
        <h2>Sign In OTP</h2>
        <p>Your OTP for signing in to StyleAI Assistant is: <strong>{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        if send_email(email, subject, body):
            return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
        else:
            return JsonResponse({'error': 'Failed to send OTP'}, status=500)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def signin_with_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return JsonResponse({'error': 'Email and OTP are required'}, status=400)
        
        # Verify OTP
        otp_obj = OTP.objects.filter(email=email, otp=otp, is_used=False).first()
        if not otp_obj:
            return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)
        
        # Check if OTP is expired (10 minutes)
        if timezone.now() - otp_obj.created_at > timedelta(minutes=10):
            return JsonResponse({'error': 'OTP expired'}, status=400)
        
        # Get user
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'gender': user.gender
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not product_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)
        
        # Get product
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return JsonResponse({'error': 'Product not found'}, status=404)
        
        # Get or create cart
        cart = None
        if user_id:
            cart = Cart.objects.filter(user_id=user_id).first()
        elif session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if not cart:
            cart = Cart.objects.create(
                user_id=user_id if user_id else None,
                session_id=session_id if session_id else None
            )
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_cart(request):
    try:
        user_id = request.GET.get('user_id')
        session_id = request.GET.get('session_id')
        
        # Get cart
        cart = None
        if user_id:
            cart = Cart.objects.filter(user_id=user_id).first()
        elif session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if not cart:
            return JsonResponse({'items': [], 'total': 0, 'count': 0})
        
        # Get cart items
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        items_data = []
        total = 0
        count = 0
        
        for item in cart_items:
            item_total = item.product.price * item.quantity
            items_data.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'image_url': item.product.image_url
                },
                'quantity': item.quantity,
                'item_total': str(item_total)
            })
            total += item_total
            count += item.quantity
        
        return JsonResponse({
            'items': items_data,
            'total': str(total),
            'count': count
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        
        if not item_id or not quantity:
            return JsonResponse({'error': 'Item ID and quantity are required'}, status=400)
        
        cart_item = CartItem.objects.filter(id=item_id).first()
        if not cart_item:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        return JsonResponse({'success': True, 'message': 'Cart updated'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        if not item_id:
            return JsonResponse({'error': 'Item ID is required'}, status=400)
        
        cart_item = CartItem.objects.filter(id=item_id).first()
        if not cart_item:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
        
        cart_item.delete()
        return JsonResponse({'success': True, 'message': 'Item removed from cart'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def profile(request):
    return render(request, 'core/profile.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_orders(request):
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)
        
        # Get user's orders
        orders = Order.objects.filter(user_id=user_id).order_by('-created_at')
        orders_data = []
        
        for order in orders:
            # Get order items
            order_items = OrderItem.objects.filter(order=order).select_related('product')
            items_data = []
            
            for item in order_items:
                items_data.append({
                    'product': {
                        'id': item.product.id,
                        'name': item.product.name,
                        'price': str(item.product.price),
                        'image_url': item.product.image_url
                    },
                    'quantity': item.quantity,
                    'item_total': str(item.product.price * item.quantity)
                })
            
            orders_data.append({
                'id': order.id,
                'status': order.status,
                'total': str(order.total),
                'created_at': order.created_at.isoformat(),
                'items': items_data
            })
        
        return JsonResponse({'orders': orders_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_order_from_cart(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        # Get cart
        cart = None
        if user_id:
            cart = Cart.objects.filter(user_id=user_id).first()
        elif session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if not cart:
            return JsonResponse({'error': 'Cart not found'}, status=404)
        
        # Get cart items
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        if not cart_items:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user_id=user_id if user_id else None,
            session_id=session_id if session_id else None,
            total=total,
            status='pending'
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Clear cart
        cart_items.delete()
        
        return JsonResponse({
            'success': True, 
            'order_id': order.id,
            'message': 'Order created successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_order_status(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        
        if not order_id or not status:
            return JsonResponse({'error': 'Order ID and status are required'}, status=400)
        
        # Update order
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        order.status = status
        order.updated_at = timezone.now()
        order.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Order status updated to {status}'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_to_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not product_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)
        
        # Build filter conditions for checking existing item
        filter_conditions = {'product_id': product_id}
        
        if user_id:
            filter_conditions['user_id'] = user_id
        elif session_id:
            filter_conditions['session_id'] = session_id
        else:
            return JsonResponse({'error': 'User ID or Session ID is required'}, status=400)
        
        # Check if already in wishlist
        existing_wishlist = Wishlist.objects.filter(**filter_conditions).first()
        
        if existing_wishlist:
            return JsonResponse({'error': 'Product already in wishlist'}, status=400)
        
        # Get product
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return JsonResponse({'error': 'Product not found'}, status=404)
        
        # Build create conditions
        create_conditions = {
            'product': product
        }
        
        if user_id:
            create_conditions['user_id'] = user_id
        else:
            create_conditions['session_id'] = session_id
        
        # Add to wishlist
        wishlist_item = Wishlist.objects.create(**create_conditions)
        
        return JsonResponse({
            'success': True, 
            'message': 'Added to wishlist',
            'wishlist_id': wishlist_item.id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_wishlist(request):
    try:
        user_id = request.GET.get('user_id')
        session_id = request.GET.get('session_id')
        
        # Build filter conditions
        filter_conditions = {}
        
        if user_id:
            filter_conditions['user_id'] = user_id
        elif session_id:
            filter_conditions['session_id'] = session_id
        else:
            return JsonResponse({'items': []})
        
        # Get wishlist items
        wishlist_items = Wishlist.objects.filter(
            **filter_conditions
        ).select_related('product').order_by('-created_at')
        
        items_data = []
        for item in wishlist_items:
            items_data.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'image_url': item.product.image_url,
                    'category': item.product.category
                },
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({'items': items_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def remove_from_wishlist(request):
    try:
        data = json.loads(request.body)
        wishlist_id = data.get('wishlist_id')
        
        if not wishlist_id:
            return JsonResponse({'error': 'Wishlist ID is required'}, status=400)
        
        wishlist_item = Wishlist.objects.filter(id=wishlist_id).first()
        if not wishlist_item:
            return JsonResponse({'error': 'Wishlist item not found'}, status=404)
        
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Removed from wishlist'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_order_from_wishlist(request):
    try:
        data = json.loads(request.body)
        wishlist_ids = data.get('wishlist_ids', [])
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not wishlist_ids:
            return JsonResponse({'error': 'No items selected'}, status=400)
        
        # Get wishlist items
        wishlist_items = Wishlist.objects.filter(id__in=wishlist_ids).select_related('product')
        if not wishlist_items:
            return JsonResponse({'error': 'No valid wishlist items found'}, status=400)
        
        # Calculate total
        total = sum(item.product.price for item in wishlist_items)
        
        # Create order
        order = Order.objects.create(
            user_id=user_id if user_id else None,
            session_id=session_id if session_id else None,
            total=total,
            status='pending'
        )
        
        # Create order items
        for item in wishlist_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=1,
                price=item.product.price
            )
        
        # Remove items from wishlist
        wishlist_items.delete()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': f'Order created with {len(wishlist_ids)} items',
            'total': str(total)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        user_id = data.get('user_id')
        
        if not order_id:
            return JsonResponse({'error': 'Order ID is required'}, status=400)
        
        # Get order
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        # Verify user owns the order
        if user_id and order.user_id != int(user_id):
            return JsonResponse({'error': 'Unauthorized to delete this order'}, status=403)
        
        # Delete order (this will also delete related OrderItems due to CASCADE)
        order.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Order deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def move_wishlist_to_cart(request):
    try:
        data = json.loads(request.body)
        wishlist_ids = data.get('wishlist_ids', [])
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not wishlist_ids:
            return JsonResponse({'error': 'No items selected'}, status=400)
        
        # Get or create cart
        cart = None
        if user_id:
            cart = Cart.objects.filter(user_id=user_id).first()
        elif session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if not cart:
            cart = Cart.objects.create(
                user_id=user_id if user_id else None,
                session_id=session_id if session_id else None
            )
        
        moved_items = []
        for wishlist_id in wishlist_ids:
            wishlist_item = Wishlist.objects.filter(id=wishlist_id).first()
            if wishlist_item:
                # Add to cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=wishlist_item.product,
                    defaults={'quantity': 1}
                )
                
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                
                moved_items.append(wishlist_item.product.name)
                wishlist_item.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Moved {len(moved_items)} items to cart',
            'items': moved_items
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
