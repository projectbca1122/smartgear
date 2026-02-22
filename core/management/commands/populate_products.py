from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Populate database with sample clothing products'

    def handle(self, *args, **options):
        products = [
            {
                'name': 'Winter Jacket for Manali',
                'description': 'Warm and waterproof jacket perfect for cold mountain destinations like Manali. Features thermal insulation and wind protection.',
                'category': 'Outerwear',
                'price': 89.99,
                'suitable_locations': 'manali, mountain, hiking, winter, cold',
                'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f324b?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Beach Shorts for Goa',
                'description': 'Comfortable quick-dry shorts ideal for beach destinations like Goa. Lightweight and stylish.',
                'category': 'Bottoms',
                'price': 29.99,
                'suitable_locations': 'goa, beach, swimming, summer, casual',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Gym Workout T-Shirt',
                'description': 'Moisture-wicking athletic t-shirt designed for intense gym sessions. Breathable and stretchable fabric.',
                'category': 'Activewear',
                'price': 24.99,
                'suitable_locations': 'gym, workout, fitness, running, training',
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Hiking Cargo Pants',
                'description': 'Durable cargo pants with multiple pockets, perfect for hiking and outdoor adventures.',
                'category': 'Bottoms',
                'price': 54.99,
                'suitable_locations': 'hiking, trekking, camping, outdoor, mountain',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Party Dress',
                'description': 'Elegant evening dress perfect for parties and special occasions. Stylish and comfortable.',
                'category': 'Formal',
                'price': 79.99,
                'suitable_locations': 'party, formal, evening, wedding, celebration',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Office Casual Shirt',
                'description': 'Professional yet comfortable shirt suitable for office wear and business meetings.',
                'category': 'Formal',
                'price': 39.99,
                'suitable_locations': 'office, business, formal, work, meeting',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Sports Running Shoes',
                'description': 'High-performance running shoes with excellent cushioning and support for all types of runs.',
                'category': 'Footwear',
                'price': 69.99,
                'suitable_locations': 'running, gym, workout, fitness, training',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Swimwear for Beach',
                'description': 'Stylish and comfortable swimwear perfect for beach destinations and swimming pools.',
                'category': 'Swimwear',
                'price': 34.99,
                'suitable_locations': 'beach, swimming, goa, pool, summer',
                'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Casual Jeans',
                'description': 'Classic denim jeans suitable for casual outings and everyday wear.',
                'category': 'Bottoms',
                'price': 49.99,
                'suitable_locations': 'casual, city, everyday, informal, travel',
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535a?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Thermal Wear for Mountains',
                'description': 'Thermal underwear set providing extra warmth for mountain destinations and cold weather.',
                'category': 'Innerwear',
                'price': 44.99,
                'suitable_locations': 'manali, mountain, winter, cold, hiking',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            # Additional 30 products
            {
                'name': 'Summer Cotton Shirt',
                'description': 'Lightweight cotton shirt perfect for summer days and casual outings.',
                'category': 'Tops',
                'price': 34.99,
                'suitable_locations': 'summer, casual, beach, goa, city',
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Yoga Leggings',
                'description': 'Comfortable and stretchable leggings designed for yoga and fitness activities.',
                'category': 'Activewear',
                'price': 42.99,
                'suitable_locations': 'yoga, gym, workout, fitness, training',
                'image_url': 'https://images.unsplash.com/photo-1540497077202-7243c69f916a?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Business Suit',
                'description': 'Professional business suit perfect for formal meetings and corporate events.',
                'category': 'Formal',
                'price': 199.99,
                'suitable_locations': 'office, business, formal, meeting, corporate',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Hiking Boots',
                'description': 'Waterproof hiking boots with excellent grip for mountain trails and trekking.',
                'category': 'Footwear',
                'price': 89.99,
                'suitable_locations': 'hiking, trekking, mountain, outdoor, camping',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Beach Sandals',
                'description': 'Comfortable sandals perfect for beach walks and summer vacations.',
                'category': 'Footwear',
                'price': 24.99,
                'suitable_locations': 'beach, goa, summer, casual, vacation',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Winter Sweater',
                'description': 'Cozy wool sweater providing warmth during cold winter days and mountain trips.',
                'category': 'Outerwear',
                'price': 59.99,
                'suitable_locations': 'winter, manali, mountain, cold, casual',
                'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Sports Shorts',
                'description': 'Athletic shorts designed for sports activities and gym workouts.',
                'category': 'Activewear',
                'price': 27.99,
                'suitable_locations': 'gym, workout, sports, fitness, training',
                'image_url': 'https://images.unsplash.com/photo-1586790170087-2f1bbad7c8c7?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Formal Trousers',
                'description': 'Elegant trousers suitable for office wear and formal occasions.',
                'category': 'Formal',
                'price': 64.99,
                'suitable_locations': 'office, business, formal, meeting, corporate',
                'image_url': 'https://images.unsplash.com/photo-1594634312652-30096f5e2fb0?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Casual Hoodie',
                'description': 'Comfortable hoodie perfect for casual outings and cool weather.',
                'category': 'Outerwear',
                'price': 44.99,
                'suitable_locations': 'casual, city, everyday, travel, informal',
                'image_url': 'https://images.unsplash.com/photo-1556821841-5bf76a0fa6ce?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Running Tank Top',
                'description': 'Lightweight tank top designed for running and intense workouts.',
                'category': 'Activewear',
                'price': 22.99,
                'suitable_locations': 'running, gym, workout, fitness, training',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Beach Cover-up',
                'description': 'Stylish cover-up dress perfect for beach destinations and poolside lounging.',
                'category': 'Swimwear',
                'price': 38.99,
                'suitable_locations': 'beach, goa, swimming, pool, summer',
                'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Denim Jacket',
                'description': 'Classic denim jacket suitable for casual outings and layering.',
                'category': 'Outerwear',
                'price': 74.99,
                'suitable_locations': 'casual, city, everyday, travel, informal',
                'image_url': 'https://images.unsplash.com/photo-1551488830-9fcef1c09744?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Gym Shorts',
                'description': 'Athletic shorts designed for gym workouts and training sessions.',
                'category': 'Activewear',
                'price': 31.99,
                'suitable_locations': 'gym, workout, fitness, training, sports',
                'image_url': 'https://images.unsplash.com/photo-1586790170087-2f1bbad7c8c7?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Formal Blazer',
                'description': 'Professional blazer perfect for business meetings and formal events.',
                'category': 'Formal',
                'price': 89.99,
                'suitable_locations': 'office, business, formal, meeting, corporate',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Mountain Backpack',
                'description': 'Durable backpack designed for hiking and mountain adventures.',
                'category': 'Accessories',
                'price': 54.99,
                'suitable_locations': 'hiking, mountain, trekking, camping, outdoor',
                'image_url': 'https://images.unsplash.com/photo-1553062407-f606588648ec?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Summer Dress',
                'description': 'Light and breezy dress perfect for summer days and beach vacations.',
                'category': 'Casual',
                'price': 49.99,
                'suitable_locations': 'summer, beach, goa, vacation, casual',
                'image_url': 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Sports Watch',
                'description': 'Digital sports watch with fitness tracking and heart rate monitoring.',
                'category': 'Accessories',
                'price': 79.99,
                'suitable_locations': 'gym, workout, fitness, running, training',
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Winter Gloves',
                'description': 'Warm insulated gloves perfect for cold weather and mountain activities.',
                'category': 'Accessories',
                'price': 24.99,
                'suitable_locations': 'winter, manali, mountain, cold, hiking',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Casual Sneakers',
                'description': 'Comfortable sneakers suitable for everyday wear and casual outings.',
                'category': 'Footwear',
                'price': 54.99,
                'suitable_locations': 'casual, city, everyday, travel, informal',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat perfect for yoga practice and floor exercises.',
                'category': 'Activewear',
                'price': 29.99,
                'suitable_locations': 'yoga, gym, workout, fitness, home',
                'image_url': 'https://images.unsplash.com/photo-1540497077202-7243c69f916a?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Beach Hat',
                'description': 'Stylish sun hat providing protection during beach days and summer outings.',
                'category': 'Accessories',
                'price': 19.99,
                'suitable_locations': 'beach, goa, summer, vacation, outdoor',
                'image_url': 'https://images.unsplash.com/photo-1525353628369-b0e5c49b8d1e?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Winter Scarf',
                'description': 'Warm wool scarf perfect for cold weather and winter fashion.',
                'category': 'Accessories',
                'price': 29.99,
                'suitable_locations': 'winter, manali, mountain, cold, casual',
                'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Sports Sunglasses',
                'description': 'UV protection sunglasses perfect for outdoor sports and beach activities.',
                'category': 'Accessories',
                'price': 44.99,
                'suitable_locations': 'beach, goa, outdoor, sports, summer',
                'image_url': 'https://images.unsplash.com/photo-1473496169904-658ba79944bb?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Gym Bag',
                'description': 'Spacious gym bag designed for carrying workout essentials and sports gear.',
                'category': 'Accessories',
                'price': 39.99,
                'suitable_locations': 'gym, workout, fitness, training, sports',
                'image_url': 'https://images.unsplash.com/photo-1553062407-f606588648ec?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Summer Shorts',
                'description': 'Lightweight shorts perfect for summer days and casual outings.',
                'category': 'Bottoms',
                'price': 32.99,
                'suitable_locations': 'summer, beach, goa, casual, vacation',
                'image_url': 'https://images.unsplash.com/photo-1586790170087-2f1bbad7c8c7?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Formal Shoes',
                'description': 'Elegant dress shoes perfect for formal events and business meetings.',
                'category': 'Footwear',
                'price': 94.99,
                'suitable_locations': 'office, business, formal, meeting, corporate',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Casual Cap',
                'description': 'Stylish baseball cap perfect for casual outings and sun protection.',
                'category': 'Accessories',
                'price': 24.99,
                'suitable_locations': 'casual, outdoor, summer, city, everyday',
                'image_url': 'https://images.unsplash.com/photo-1525353628369-b0e5c49b8d1e?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Winter Boots',
                'description': 'Insulated boots perfect for cold weather and winter activities.',
                'category': 'Footwear',
                'price': 84.99,
                'suitable_locations': 'winter, manali, mountain, cold, outdoor',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Gym Water Bottle',
                'description': 'Insulated water bottle designed for gym workouts and hydration.',
                'category': 'Accessories',
                'price': 19.99,
                'suitable_locations': 'gym, workout, fitness, training, sports',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Beach Towel',
                'description': 'Quick-dry beach towel perfect for swimming and beach activities.',
                'category': 'Accessories',
                'price': 22.99,
                'suitable_locations': 'beach, goa, swimming, pool, summer',
                'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&crop=entropy&auto=format'
            },
            {
                'name': 'Winter Beanie',
                'description': 'Warm beanie hat perfect for cold weather and winter fashion.',
                'category': 'Accessories',
                'price': 27.99,
                'suitable_locations': 'winter, manali, mountain, cold, casual',
                'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=entropy&auto=format'
            }
        ]

        created_count = 0
        for product_data in products:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new products!')
        )
