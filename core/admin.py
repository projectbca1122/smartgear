from django.contrib import admin
from .models import Product, User, Cart, CartItem, OTP

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'image_thumbnail', 'suitable_locations', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'suitable_locations')
    list_editable = ('price', 'suitable_locations')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def image_thumbnail(self, obj):
        if obj.image_url:
            return f'<img src="{obj.image_url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />'
        return 'No image'
    image_thumbnail.short_description = 'Product image thumbnail'
    
    def formatted_price(self, obj):
        return f"₹{obj.price:.2f}"
    formatted_price.short_description = 'Price with rupee symbol'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('Product Details', {
            'fields': ('suitable_locations', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'gender', 'is_verified', 'created_at')
    list_filter = ('gender', 'is_verified', 'created_at')
    search_fields = ('name', 'email')
    list_editable = ('is_verified',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'gender')
        }),
        ('Account Status', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ('created_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'created_at')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name',)
    list_editable = ('quantity',)
    ordering = ('-added_at',)
    readonly_fields = ('added_at',)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
