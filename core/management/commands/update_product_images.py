from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Update image URLs for specific products'

    def handle(self, *args, **options):
        # Product name to image URL mapping
        product_updates = {
            'Beach Shirt - Hawaiian': 'https://images.pexels.com/photos/6311392/pexels-photo-6311392.jpeg',
            'Cotton Vest - Sleeveless': 'https://images.pexels.com/photos/6311613/pexels-photo-6311613.jpeg',
            'Tank Top - Athletic': 'https://images.pexels.com/photos/416778/pexels-photo-416778.jpeg',
            'Cotton T-Shirt - Summer Breeze': 'https://images.pexels.com/photos/6311393/pexels-photo-6311393.jpeg',
            'Polo Shirt - Sport Edition': 'https://images.pexels.com/photos/5698851/pexels-photo-5698851.jpeg',
            'Casual Shirt - Office Ready': 'https://images.pexels.com/photos/1043474/pexels-photo-1043474.jpeg',
            'Linen Shirt - Beach Style': 'https://images.pexels.com/photos/974746/pexels-photo-974746.jpeg',
            'Dress Shirt - French Cuff': 'https://images.pexels.com/photos/1043473/pexels-photo-1043473.jpeg',
            'Linen Shorts - Casual': 'https://images.pexels.com/photos/6311387/pexels-photo-6311387.jpeg',
            'Summer Shorts - Beach Ready': 'https://images.pexels.com/photos/1884584/pexels-photo-1884584.jpeg',
            'Chino Pants - Slim Fit': 'https://images.pexels.com/photos/6311396/pexels-photo-6311396.jpeg',
            'Track Pants - Athletic': 'https://images.pexels.com/photos/6311388/pexels-photo-6311388.jpeg',
            'Yoga Leggings - Flexible': 'https://images.pexels.com/photos/4056535/pexels-photo-4056535.jpeg',
            'Denim Jeans - Classic Fit': 'https://images.pexels.com/photos/52518/jeans-clothing-blue-pants-52518.jpeg',
            'Light Jacket - Travel': 'https://images.pexels.com/photos/6311605/pexels-photo-6311605.jpeg',
            'Windbreaker - Light': 'https://images.pexels.com/photos/6311606/pexels-photo-6311606.jpeg',
            'Denim Jacket - Classic': 'https://images.pexels.com/photos/6311607/pexels-photo-6311607.jpeg',
            'Casual Blazer - Modern': 'https://images.pexels.com/photos/1043475/pexels-photo-1043475.jpeg',
            'Light Hoodie - Comfort Fit': 'https://images.pexels.com/photos/6311608/pexels-photo-6311608.jpeg',
            'Sports Sandals - Outdoor': 'https://images.pexels.com/photos/19090/pexels-photo.jpg',
            'Sandals - Leather': 'https://images.pexels.com/photos/19090/pexels-photo.jpg',
            'Training Shoes - CrossFit': 'https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg',
            'Sneakers - Urban Style': 'https://images.pexels.com/photos/2529118/pexels-photo-2529118.jpeg',
            'Business Shoes - Leather': 'https://images.pexels.com/photos/267301/pexels-photo-267301.jpeg',
            'Hiking Boots - Waterproof': 'https://images.pexels.com/photos/19090/pexels-photo.jpg',
            'Flip Flops - Beach': 'https://images.pexels.com/photos/918063/pexels-photo-918063.jpeg',
            'Cotton Cap - Sporty': 'https://images.pexels.com/photos/6311615/pexels-photo-6311615.jpeg',
            'Sports Watch - Digital': 'https://images.pexels.com/photos/358850/pexels-photo-358850.jpeg',
            'Sunglasses - Polarized': 'https://images.pexels.com/photos/46710/pexels-photo-46710.jpeg',
            'Business Belt - Leather': 'https://images.pexels.com/photos/45055/pexels-photo-45055.jpeg',
            'Neck Pillow - Travel': 'https://images.pexels.com/photos/1552252/pexels-photo-1552252.jpeg',
            'Camping Tent - 2 Person': 'https://images.pexels.com/photos/2398220/pexels-photo-2398220.jpeg',
            'Sleeping Bag - Cold Weather': 'https://images.pexels.com/photos/1552252/pexels-photo-1552252.jpeg',
            'Hiking Backpack - 40L': 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg',
            'Outdoor Vest - Multi Pocket': 'https://images.pexels.com/photos/1183261/pexels-photo-1183261.jpeg',
            'Track Suit - Complete': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg',
            'Gym Hoodie - Training': 'https://images.pexels.com/photos/6311608/pexels-photo-6311608.jpeg',
            'Compression Shorts - Gym': 'https://images.pexels.com/photos/1884584/pexels-photo-1884584.jpeg',
            'Gym Tank Top - Performance': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg',
            'Football Jersey - Pro': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg',
            'Cotton Saree - Elegant': 'https://images.pexels.com/photos/6311618/pexels-photo-6311618.jpeg',
            'Cotton Kurta - Traditional': 'https://images.pexels.com/photos/9986412/pexels-photo-9986412.jpeg',
            'Kurta Pyjama - Cotton': 'https://images.pexels.com/photos/9986412/pexels-photo-9986412.jpeg',
            'Sherwani - Traditional': 'https://images.pexels.com/photos/9986412/pexels-photo-9986412.jpeg',
            'Nehru Jacket - Classic': 'https://images.pexels.com/photos/1043475/pexels-photo-1043475.jpeg'
        }

        updated_count = 0
        not_found_count = 0

        self.stdout.write(self.style.SUCCESS('Starting product image updates...'))

        for product_name, image_url in product_updates.items():
            # Find all products with this name (handles duplicates)
            products = Product.objects.filter(name=product_name)
            
            if products.exists():
                for product in products:
                    # Update the image URL
                    old_image_url = product.image_url
                    product.image_url = image_url
                    product.save()
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated: {product_name} (ID: {product.id})\n'
                            f'  Old: {old_image_url}\n'
                            f'  New: {image_url}'
                        )
                    )
            else:
                not_found_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Product not found: {product_name}')
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Update Summary:'))
        self.stdout.write(f'  Products updated: {updated_count}')
        self.stdout.write(f'  Products not found: {not_found_count}')
        self.stdout.write('='*50)
