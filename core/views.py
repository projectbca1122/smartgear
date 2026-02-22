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
from django.db.models import Sum, F
from django.utils import timezone
from google.generativeai import configure, GenerativeModel
from .models import Product, User, Cart, CartItem, OTP
import random
import hashlib
from datetime import timedelta, datetime

# Configure Gemini API
API_KEY = "AIzaSyDep7ViZrClZgjRt1B2S1QxUkcyr6NS0OY"
configure(api_key=API_KEY)
model = GenerativeModel("gemini-2.5-flash")

# Initialize text-to-speech engine
engine = pyttsx3.init()

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
        
        # Find relevant products based on user message
        products = find_relevant_products(user_message)
        
        response_data = {
            'ai_response': ai_response,
            'products': [
                {
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

def get_ai_response(user_message):
    try:
        # Find relevant products based on user message
        relevant_products = find_relevant_products(user_message)
        
        if relevant_products:
            response = "Here are the products matching your request:\n\n"
            for i, product in enumerate(relevant_products, 1):
                response += f"{i}. {product.name}\n"
                response += f"   - Price: ₹{product.price:.2f}\n"
                response += f"   - Category: {product.category}\n"
                response += f"   - Perfect for: {product.suitable_locations}\n\n"
            return response
        else:
            return "I apologize, but I could not find products matching your request. Please try with different keywords like 'hiking', 'beach', 'gym', etc."
    
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"

def find_relevant_products(user_message):
    # Extract location/activity keywords from user message
    keywords = []
    locations = ['manali', 'goa', 'gym', 'hiking', 'beach', 'mountain', 'city', 'office', 'party', 'casual','business']
    activities = ['trekking', 'swimming', 'workout', 'running', 'camping', 'travel', 'formal', 'informal']
    product_types = ['shoes', 'shirt', 'pants', 'jacket', 'dress', 'shorts', 'top', 'sweater']
    
    user_message_lower = user_message.lower()
    
    # First check for exact product name matches
    products = Product.objects.all()
    relevant_products = []
    
    # Split user message into individual words
    user_words = user_message_lower.split()
    
    for product in products:
        product_name_lower = product.name.lower()
        # Split product name into individual words
        product_words = product_name_lower.split()
        
        # Check if any user word matches any product word
        word_match = False
        for user_word in user_words:
            for product_word in product_words:
                if user_word == product_word:
                    word_match = True
                    break
            if word_match:
                break
        
        # Also check if full product name is mentioned
        full_name_match = product_name_lower in user_message_lower
        
        if word_match or full_name_match:
            relevant_products.append(product)
            continue
    
    # Always check for location/activity matches in ALL products and add them too
    additional_products = []
    for product in products:
        if product not in relevant_products:  # Avoid duplicates
            product_text = f"{product.name.lower()} {product.description.lower()} {product.suitable_locations.lower()}"
            
            # Check for locations
            for location in locations:
                if location in user_message_lower and location in product_text:
                    additional_products.append(product)
                    break
            
            # Check for activities
            for activity in activities:
                if activity in user_message_lower and activity in product_text:
                    additional_products.append(product)
                    break
            
            # Check for product types
            for product_type in product_types:
                if product_type in user_message_lower and product_type in product_text:         
                    additional_products.append(product)
                    break
    
    # Combine both lists
    all_relevant_products = relevant_products + additional_products
    
    # Remove duplicates while preserving order
    seen = set()
    final_products = []
    for product in all_relevant_products:
        if product.id not in seen:
            seen.add(product.id)
            final_products.append(product)
    
    # If no specific products found, return some general recommendations
    if not final_products:
        final_products = products[:5]
    
    return final_products[:10]  # Return max 10 products to show more

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
        
        return JsonResponse({'success': True, 'message': 'Account created successfully'})
    
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
