import json
import speech_recognition as sr
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
API_KEY = "AIzaSyCZ9UYXNVkEBpGQO8mfLe_DpBs_sH5yWaM"
configure(api_key=API_KEY)
model = GenerativeModel("gemini-2.5-flash")

# Weather API configuration
WEATHER_API_KEY = "e0f58f02ae07966898ecf53c37dca217"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Text-to-speech engine (lazy initialization)
_tts_engine = None

def _get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        try:
            import pyttsx3
            _tts_engine = pyttsx3.init()
        except Exception:
            pass
    return _tts_engine

# Conversation memory and context
user_context = {
    "name": None,
    "last_location": None,
    "last_activity": None
}

# STOPWORDS - Remove useless words that match everything
STOPWORDS = {
    "i", "am", "is", "are", "was", "were", "to", "the", "a", "an", "and", "or",
    "going", "want", "need", "for", "in", "on", "me", "my", "we", "you",
    "at", "of", "with", "from", "by", "as", "be", "have", "has", "had"
}

# LAYER 1: RULE ENGINE (NO AI)
INTENT_MAP = {
    "activity": ["gym", "hiking", "party", "travel", "casual", "formal", "beach", "sports", "business", "outdoor", "trekking", "swimming", "workout", "running", "camping", "yoga"],
    "product_type": [
        "shirt", "jacket", "hoodie", "shoes", "jeans", "pants", "dress", "shorts", 
        "top", "sweater", "t-shirt", "trousers", "coat", "sports wear", "ethnic wear", 
        "sandals", "boots", "sneakers", "blazer", "suit", "kurta", "leggings", 
        "yoga pants", "track pants", "cap", "hat", "belt", "socks", "gloves", "scarf",
        "saree", "lehenga", "sherwani", "vest", "cardigan", "windbreaker", "raincoat"
    ]
}

def get_clean_keywords(message):
    """Extract meaningful keywords from message"""
    words = message.lower().split()
    keywords = []
    
    for word in words:
        # Skip stopwords and short words
        if word not in STOPWORDS and len(word) > 2:
            keywords.append(word)
    
    return keywords

def extract_intent(message):
    """Extract intent using rules and regex (NO AI)"""
    msg = message.lower()
    
    # Extract activity
    activity = None
    for act in INTENT_MAP["activity"]:
        if act in msg:
            activity = act
            break
    
    # Extract product type
    product_type = None
    for prod in INTENT_MAP["product_type"]:
        if prod in msg:
            product_type = prod
            break
    
    # Extract location
    location = extract_location_from_message(message)
    
    intent = {
        "activity": activity,
        "product_type": product_type,
        "location": location[0] if location else None
    }
    
    # Update context
    if intent["location"]:
        user_context["last_location"] = intent["location"]
    if intent["activity"]:
        user_context["last_activity"] = intent["activity"]
    
    return intent

# LAYER 2: TEMPERATURE CATEGORY MAPPING
def map_temp_category(temp):
    """Convert temperature to category"""
    if temp < 12:
        return "cold"
    elif temp < 25:
        return "moderate"
    else:
        return "hot"

# LAYER 3: STRICT SCORING ENGINE
def score_product(product, intent, temp_category, user_message=""):
    """Score product based on intent and temperature (NO AI)"""
    score = 0
    
    # TEMP MATCH (HIGHEST PRIORITY)
    if temp_category and product.temp_category and temp_category == product.temp_category:
        score += 50
        print(f"DEBUG: TEMP MATCH! {temp_category} == {product.temp_category}")
    
    # CLEAN WORD-LEVEL PRODUCT NAME MATCHING
    if user_message:
        keywords = get_clean_keywords(user_message)
        product_name_words = product.name.lower().split()
        
        # EXACT WORD MATCHING ONLY
        for keyword in keywords:
            if keyword in product_name_words:  # Exact match only
                score += 30
                print(f"DEBUG: EXACT WORD MATCH! '{keyword}' matches in {product.name}")
    
    # PRODUCT TYPE (high weight)
    if intent["product_type"] and intent["product_type"] in product.name.lower():
        score += 40
        print(f"DEBUG: PRODUCT TYPE MATCH! {intent['product_type']} in {product.name}")
    
    # ACTIVITY (medium weight)
    if intent["activity"]:
        if product.activity_tag and intent["activity"] == product.activity_tag:
            score += 30
            print(f"DEBUG: ACTIVITY MATCH! {intent['activity']} == {product.activity_tag}")
        elif intent["activity"] in product.description.lower():
            score += 20
        elif intent["activity"] in product.name.lower():
            score += 15
    
    # LOCATION relevance (medium weight)
    if intent["location"] and intent["location"] in product.suitable_locations.lower():
        score += 20
        print(f"DEBUG: LOCATION MATCH! {intent['location']} in {product.suitable_locations}")
    
    # Priority boost (optional)
    if product.priority_score:
        score += product.priority_score
        print(f"DEBUG: PRIORITY BOOST! +{product.priority_score}")
    
    return score

def simple_search_products(message):
    """Simple search: find products containing search words in their names (flexible matching)"""
    print(f"DEBUG: Simple search for: '{message}'")
    
    # Clean the message: remove punctuation and convert to lowercase
    import string
    cleaned_message = message.lower().translate(str.maketrans('', '', string.punctuation))
    words = cleaned_message.split()
    
    # Remove common words that aren't product names
    stop_words = {"i", "want", "need", "show", "me", "get", "give", "looking", "for", "the", "a", "an", "and", "or", "to", "at", "in", "on", "with", "from", "by", "as", "be", "have", "has", "had", "am", "is", "are", "was", "were"}
    search_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    print(f"DEBUG: Search words: {search_words}")
    
    if not search_words:
        return None
    
    # Create variations of search words (singular/plural)
    all_search_variations = []
    for word in search_words:
        all_search_variations.append(word)
        
        # Add singular version if word is plural
        if word.endswith('s') and len(word) > 3:
            singular = word[:-1]  # Remove 's' from end
            if singular not in all_search_variations:
                all_search_variations.append(singular)
        
        # Add plural version if word is singular
        elif not word.endswith('s') and len(word) > 2:
            plural = word + 's'  # Add 's' to end
            if plural not in all_search_variations:
                all_search_variations.append(plural)
    
    print(f"DEBUG: All search variations: {all_search_variations}")
    
    # Find products that contain ANY of the search variations in their name
    matched_products = {}
    for word in all_search_variations:
        products = Product.objects.filter(name__icontains=word)
        for product in products:
            if product not in matched_products:
                matched_products[product] = 0  # Initialize score
            matched_products[product] += 1  # Increment score for each match
    
    if matched_products:
        # Sort by number of matches (highest first)
        sorted_products = sorted(matched_products.items(), key=lambda x: x[1], reverse=True)
        result_products = [product for product, score in sorted_products]
        
        print(f"DEBUG: Found {len(result_products)} matching products: {[p.name for p in result_products]}")
        return result_products
    
    return None

def get_best_products(message):
    """Get best products - try simple search first, then fallback to complex logic"""
    print(f"DEBUG: Processing message: '{message}'")
    
    # PRIORITY 0: Try simple direct search first
    simple_results = simple_search_products(message)
    if simple_results:
        print(f"DEBUG: Simple search found products, returning them")
        return simple_results[:5]  # Return up to 5 matching products
    
    # PRIORITY 1: Check for "I want X" patterns - direct product name matching
    direct_match_products = check_direct_product_match(message)
    if direct_match_products:
        print(f"DEBUG: Direct product match found: {[p.name for p in direct_match_products]}")
        # Return only the top 3 matching products for direct searches
        return direct_match_products[:3]
    
    # LAYER 1: Extract intent (RULES ONLY)
    intent = extract_intent(message)
    print(f"DEBUG: Extracted intent: {intent}")
    
    # AI FALLBACK: Only activate if rule system finds NOTHING
    has_any_intent = intent["product_type"] or intent["activity"] or intent["location"]
    if not has_any_intent:
        print("DEBUG: No intent found, calling AI fallback")
        ai_intent = extract_intent_with_gemini(message)
        if ai_intent:
            # Merge AI intent with rule intent
            intent.update({k: v for k, v in ai_intent.items() if v})
            print(f"DEBUG: Merged AI intent: {intent}")
    else:
        print("DEBUG: Intent extracted successfully, skipping AI")
    
    # LAYER 2: Get weather and temperature category
    weather = None
    temp_category = None
    if intent["location"]:
        weather = get_weather_info(intent["location"])
        if weather and weather.get('success'):
            temp_category = map_temp_category(weather["temperature"])
            print(f"DEBUG: Weather: {weather['temperature']}°C -> {temp_category}")
    
    # HANDLE "ONLY LOCATION" CASE (PURE WEATHER-BASED)
    if not intent["activity"] and not intent["product_type"] and temp_category:
        print(f"DEBUG: Pure weather-based recommendation for {temp_category}")
        weather_products = Product.objects.filter(temp_category=temp_category)
        print(f"DEBUG: Found {weather_products.count()} weather-matched products")
        
        # Get random 10 products from the temperature category
        weather_products_list = list(weather_products)
        random.shuffle(weather_products_list)
        random_products = weather_products_list[:10]
        print(f"DEBUG: Returning {len(random_products)} random products from {temp_category} category")
        return random_products
    
    # GET ALL PRODUCTS AND SCORE THEM
    products = Product.objects.all()
    print(f"DEBUG: Total products to score: {products.count()}")
    
    scored = []
    
    for p in products:
        s = score_product(p, intent, temp_category, message)
        print(f"DEBUG: Product '{p.name}' - Score: {s}")
        
        # ACCEPT SCORES - realistic threshold
        if s >= 30:
            scored.append((s, p))
            print(f"DEBUG: ACCEPTED: '{p.name}' with score {s}")
    
    print(f"DEBUG: Total accepted products: {len(scored)}")
    
    # If no products scored, return top 10 by any score
    if not scored:
        print("DEBUG: No products scored, returning top 10 anyway")
        for p in products:
            s = score_product(p, intent, temp_category, message)
            scored.append((s, p))
    
    # Sort by score (highest first) and return top 10
    scored.sort(reverse=True, key=lambda x: x[0])
    
    result = [p for _, p in scored[:10]]
    print(f"DEBUG: Returning {len(result)} products: {[p.name for p in result]}")
    return result

def check_direct_product_match(message):
    """Check for direct product name matches in 'I want X' patterns or direct product searches"""
    msg = message.lower()
    
    # Check for "I want X" patterns
    want_patterns = ["i want", "i need", "show me", "get me", "give me", "looking for"]
    
    for pattern in want_patterns:
        if pattern in msg:
            # Extract the product name after the pattern
            product_part = msg.split(pattern, 1)[1].strip()
            if product_part:
                return find_products_by_keywords(product_part)
    
    # Also check for direct product searches without patterns (like "water bottle", "jacket", etc.)
    # Only if the message is short and seems like a product search
    words = msg.split()
    if len(words) <= 4:  # Short messages are likely direct product searches
        # Skip common non-product words
        non_product_words = {"hello", "hi", "hey", "thanks", "bye", "help", "who", "what", "where", "when", "how", "why", "are", "is", "am", "the", "a", "an"}
        filtered_words = [w for w in words if w not in non_product_words and len(w) > 2]
        
        if filtered_words:
            # Check if any words match product types or categories
            product_indicators = ["shirt", "pants", "shoes", "jacket", "dress", "bottle", "bag", "watch", "wallet", "hat", "cap", "belt", "socks", "gloves", "scarf"]
            if any(word in product_indicators for word in filtered_words):
                return find_products_by_keywords(msg)
    
    return None

def find_products_by_keywords(search_text):
    """Find products by keywords with precise matching"""
    keywords = get_clean_keywords(search_text)
    print(f"DEBUG: Searching for keywords: {keywords}")
    
    if not keywords:
        return None
    
    matched_products = {}
    
    # First, try exact phrase matching
    search_lower = search_text.lower()
    for product in Product.objects.all():
        product_name_lower = product.name.lower()
        
        # Exact phrase match in product name (highest priority)
        if search_lower in product_name_lower:
            matched_products[product] = 100  # Very high score for exact phrase
            continue
        
        # Check individual keywords with higher precision
        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Exact word match in product name (high priority)
            if keyword_lower in product_name_lower:
                # Bonus for exact word matches
                if keyword_lower == product_name_lower.split()[-1]:  # Last word match
                    score += 30
                else:
                    score += 20
            
            # Partial match in product name (lower priority)
            elif keyword_lower in product_name_lower:
                score += 5
            
            # Description match (much lower priority)
            elif keyword_lower in product.description.lower():
                score += 2
            
            # Category match (lowest priority)
            elif keyword_lower in product.category.lower():
                score += 1
        
        if score > 0:
            matched_products[product] = score
    
    if matched_products:
        # Sort by relevance score
        sorted_products = sorted(matched_products.items(), key=lambda x: x[1], reverse=True)
        result_products = [product for product, score in sorted_products]
        
        # If we have an exact phrase match, return only the top 1-2
        top_score = sorted_products[0][1]
        if top_score >= 100:  # Exact phrase match
            print(f"DEBUG: Exact phrase match found: {result_products[0].name}")
            return result_products[:2]
        
        print(f"DEBUG: Direct match products found: {[p.name for p in result_products[:3]]}")
        return result_products[:3]  # Return top 3 most relevant matches
    
    return None

def extract_name(message):
    """Extract user name from message"""
    match = re.search(r"my name is (\w+)", message.lower())
    return match.group(1).capitalize() if match else None

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

def extract_intent_with_gemini(user_message):
    """AI fallback intent extraction - ONLY used when rule system fails"""
    try:
        prompt = f"""You are a strict JSON extractor.

Extract intent from user message.

Return ONLY JSON:

{{
  "location": "",
  "activity": "",
  "product_type": "",
  "temperature_preference": "hot|cold|moderate"
}}

Rules:
- Do NOT guess randomly
- Leave fields empty if not clear
- Be precise and minimal

User message: "{user_message}"
"""

        response = model.generate_content(prompt)

        text = response.text.strip()

        # CLEAN JSON (Gemini sometimes adds ```json)
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print("Gemini fallback error:", e)
        return None

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

def get_weather_based_products(weather_info, user_message, base_products=None):
    """Get product recommendations based on weather conditions"""
    temp = weather_info['temperature']
    description = weather_info['description'].lower()
    location = weather_info.get('location', '').lower()
    
    # Use base_products if provided, otherwise get all
    products = base_products if base_products is not None else Product.objects.all()
    relevant_products = []
    
    for product in products:
        product_text = f"{product.name.lower()} {product.description.lower()} {product.suitable_locations.lower()}"
        
        # HARD FILTER FIRST (THIS IS THE FIX)
        if temp < 10:
            if not any(word in product_text for word in ['jacket', 'thermal', 'winter', 'hoodie', 'sweater']):
                continue
        elif temp < 20:
            if not any(word in product_text for word in ['jacket', 'full sleeve', 'layer']):
                continue
        elif temp > 30:
            if not any(word in product_text for word in ['shorts', 'tshirt', 'summer', 'light']):
                continue
        
        relevant_products.append(product)
    
    return relevant_products[:8]

@csrf_exempt
@require_http_methods(["POST"])
def voice_assistant(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Extract location and get weather first
        locations = extract_location_from_message(user_message)
        weather_info = None
        
        if locations:
            weather_info = get_weather_info(locations[0])
        
        # Get products using new 3-layer architecture
        products = get_best_products(user_message)
        
        # Generate AI response with weather context
        if weather_info and weather_info.get('success'):
            try:
                ai_response = generate_chat_response(user_message, weather_info, products)
                temperature = weather_info.get('temperature')
            except Exception as e:
                # Gemini failed, use fallback with temperature
                print(f"Gemini chat failed: {e}")
                ai_response = get_ai_response_with_temp(user_message, weather_info)
                temperature = weather_info.get('temperature')
        else:
            ai_response = get_ai_response(user_message)
            temperature = None
        
        # Get top product for highlighting
        top_product = products[0] if products else None
        
        response_data = {
            'ai_response': ai_response,
            'temperature': temperature,
            'highlight_product': {
                'id': top_product.id,
                'name': top_product.name,
                'description': top_product.description,
                'category': top_product.category,
                'price': str(top_product.price),
                'image_url': top_product.image_url
            } if top_product else None,
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
    """Get products using AI-driven structured intent extraction"""
    # Extract structured intent using Gemini
    intent = extract_intent_with_gemini(user_message)
    
    if not intent:
        # Fallback to old method if AI fails
        return find_relevant_products(user_message)[:8]
    
    location = intent.get("location")
    activity = intent.get("activity")
    product_type = intent.get("product_type")
    temp_preference = intent.get("temperature_preference")
    
    # Start with all products
    products = Product.objects.all()
    
    # STRICT FILTER FIRST (PRIORITY ORDER)
    # 1. Product Type (highest priority)
    if product_type:
        products = products.filter(
            Q(category__icontains=product_type) |
            Q(name__icontains=product_type)
        )
    
    # 2. Activity (second priority)
    if activity:
        products = products.filter(
            Q(category__icontains=activity) |
            Q(description__icontains=activity) |
            Q(suitable_locations__icontains=activity)
        )
    
    # 3. Location (third priority)
    if location:
        products = products.filter(
            Q(suitable_locations__icontains=location)
        )
    
    # 4. Weather (last filter, ONLY if results exist)
    if location and products.exists():
        weather_info = get_weather_info(location)
        if weather_info['success']:
            # Apply temperature-based hard filtering to already filtered products
            weather_products = get_weather_based_products(weather_info, user_message, products)
            if weather_products:
                return weather_products[:8]
    
    # Return filtered results or fallback
    result = products[:8] if products.exists() else find_relevant_products(user_message)[:8]
    return result

def generate_chat_response(user_message, weather_info, products):
    try:
        # Get the actual product names that are being shown
        if products and len(products) > 0:
            product_names = [p.name for p in products[:5]]  # Use first 5 products
            
            # Create simple product list text
            if len(product_names) == 1:
                product_text = product_names[0]
            elif len(product_names) == 2:
                product_text = f"{product_names[0]} and {product_names[1]}"
            elif len(product_names) > 2:
                product_text = f"{', '.join(product_names[:-1])}, and {product_names[-1]}"
            else:
                product_text = ""
            
            # Simple response using ONLY the shown products
            if weather_info and weather_info.get('success'):
                temp = weather_info.get('temperature')
                location = weather_info.get('location', 'your location')
                response = f"The weather in {location} is currently {temp}°C. Here are some recommend products: {product_text}"
            else:
                response = f"Here are some recommend products: {product_text}"
        else:
            response = "Sorry, I couldn't find any products matching your request."
        
        return response

    except Exception as e:
        print(f"Error in generate_chat_response: {e}")
        # Simple fallback
        if products and len(products) > 0:
            return f"Here are some recommend products: {products[0].name}"
        else:
            return "Sorry, I couldn't find any products matching your request."

def generate_smart_response(user_message, weather_info):
    try:
        # Simple, direct response without AI
        if weather_info and weather_info.get('success'):
            temp = weather_info.get('temperature')
            location = weather_info.get('location', 'your location')
            
            # Direct temperature statement and recommendation
            response = f"The weather in {location} is currently {temp}°C. Here are some recommend products for you."
        else:
            response = "Here are some recommend products for you!"
        
        return response

    except Exception as e:
        print(f"Error in generate_smart_response: {e}")
        return "Here are some recommend products for you!"

def get_ai_response_with_temp(user_message, weather_info):
    """Fallback AI response that includes temperature when Gemini fails"""
    try:
        user_message_lower = user_message.lower().strip()
        name = user_context.get("name", "")
        temp = weather_info.get('temperature', 'unknown')
        location = weather_info.get('location', 'your destination')
        
        # Simple temperature-aware responses
        if temp != 'unknown':
            if temp < 10:
                response = f"Hey {name if name else 'there'}! It's quite cold in {location} right now ({temp}°C). I'd recommend warm layers like jackets and thermals. Let me find some great options for you!"
            elif temp < 20:
                response = f"Hi {name if name else 'there'}! It's cool in {location} ({temp}°C). You'll want something comfortable like light jackets or sweaters. Here are some suggestions!"
            elif temp > 30:
                response = f"Hey {name if name else 'there'}! It's quite hot in {location} ({temp}°C). You'll want something light and breathable. Let me show you some great options!"
            else:
                response = f"Hi {name if name else 'there'}! The weather in {location} is nice ({temp}°C). Here are some perfect products for you!"
        else:
            response = f"Hey {name if name else 'there'}! I found some great options for {location}. Let me show you what I recommend!"
        
        return response
        
    except Exception as e:
        print(f"Fallback response error: {e}")
        return f"Here are some great options for your trip to {weather_info.get('location', 'your destination')}!"

def get_ai_response(user_message):
    try:
        user_message_lower = user_message.lower().strip()
        
        # Extract and store user name
        name = extract_name(user_message)
        if name:
            user_context['name'] = name
            return f"Hey {name} 👋 Nice to meet you! Are you planning a trip or looking for something specific?"
        
        # Handle greetings with personalization
        greetings = ['hey', 'hello', 'hi there','good morning', 'good afternoon', 'good evening']
        if any(greeting in user_message_lower for greeting in greetings):
            name = user_context.get("name", "")
            try:
                # Use Gemini to generate contextual greeting response
                gemini_response = model.generate_content(f"Generate a friendly, personalized greeting response for SmartGear AI assistant. The user said: '{user_message}'. User name: {name}. Keep it brief and mention that I can help with weather-based product recommendations.")
                return gemini_response.text
            except:
                # Fallback to static responses if AI fails
                if name:
                    responses = [
                        f"Hello {name}! I'm your SmartGear assistant. I can help you find perfect products based on weather and location! Just tell me where you're going.",
                        f"Hi {name}! I'm your smart shopping assistant. I can check weather conditions and suggest the perfect gear for your trip!",
                        f"Hey {name}! Welcome to SmartGear. Tell me about your travel plans and I'll recommend the best products for the weather!"
                    ]
                else:
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
        
        # Use AI-driven intent extraction for intelligent processing
        intent = extract_intent_with_gemini(user_message)
        
        if intent and intent.get("location"):
            location = intent["location"]
            weather_info = get_weather_info(location)
            
            if weather_info['success']:
                try:
                    # Get products for this location
                    products = get_consistent_products(user_message)
                    
                    # Generate natural conversational response
                    return generate_chat_response(user_message, weather_info, products)
                except Exception as e:
                    # Gemini chat failed, use fallback with temperature
                    print(f"Gemini chat failed in get_ai_response: {e}")
                    return get_ai_response_with_temp(user_message, weather_info)
            else:
                # Weather API failed, but we still have location
                name = user_context.get("name", "")
                return f"{name if name else 'There'}, I found some great options for {location.title()}. What type of activity are you planning there?"
        
        # Add follow-up logic for specific locations
        if "kashmir" in user_message.lower():
            name = user_context.get("name", "")
            return f"{name if name else 'It'}'s quite cold there ❄️ Do you need heavy winter wear or something lightweight for travel?"
        
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
        tts = _get_tts_engine()
        if tts:
            tts.say(text)
            tts.runAndWait()
        
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
