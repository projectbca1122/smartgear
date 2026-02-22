from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/voice-assistant/', views.voice_assistant, name='voice_assistant'),
    path('api/text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('api/products/', views.get_products, name='get_products'),
    
    # Authentication URLs
    path('api/send-otp/', views.send_otp, name='send_otp'),
    path('api/verify-otp-signup/', views.verify_otp_and_signup, name='verify_otp_and_signup'),
    path('api/signin-password/', views.signin_with_password, name='signin_with_password'),
    path('api/send-signin-otp/', views.send_signin_otp, name='send_signin_otp'),
    path('api/signin-otp/', views.signin_with_otp, name='signin_with_otp'),
    
    # Cart URLs
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/get-cart/', views.get_cart, name='get_cart'),
    path('api/update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
]
