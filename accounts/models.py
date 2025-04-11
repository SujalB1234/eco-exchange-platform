import os
from django.db import models
from django.contrib.auth.models import User

def product_image_upload_to(instance, filename):
    """Generate a dynamic path for product image upload"""
    base_filename, file_extension = os.path.splitext(filename)
    return f'product_images/{instance.name}/{base_filename}_{instance.id}{file_extension}'

class UserProfile(models.Model):
    """User profile model to store additional information like profile picture and bio"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Category(models.Model):
    """Category model for product classification"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model for managing products being sold, exchanged, or donated"""
    STATUS_CHOICES = [
        ('for_sale', 'For Sale'),
        ('for_exchange', 'For Exchange'),
        ('for_donation', 'For Donation'),
        ('Recycling', 'For Recycling'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to=product_image_upload_to, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Eco-impact fields
    estimated_co2_saving = models.FloatField(
        default=0,
        help_text="Estimated CO2 savings in kg",
        blank=True,
        null=True
    )
    estimated_water_saving = models.FloatField(
        default=0,
        help_text="Estimated water savings in liters",
        blank=True,
        null=True
    )
    estimated_waste_reduction = models.FloatField(
        default=0,
        help_text="Estimated waste reduction in kg",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

class EcoImpact(models.Model):
    """Model to track environmental impact of user actions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eco_impacts')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Associated product if impact is from a product"
    )
    recyclable_item = models.ForeignKey(
        'RecyclableItem', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Associated recyclable item if impact is from recycling"
    )
    date_recorded = models.DateTimeField(auto_now_add=True)
    
    # Impact Metrics
    co2_saved_kg = models.FloatField(
        default=0,
        help_text="CO2 saved in kilograms"
    )
    water_saved_liters = models.FloatField(
        default=0,
        help_text="Water saved in liters"
    )
    waste_diverted_kg = models.FloatField(
        default=0,
        help_text="Waste diverted from landfills in kg"
    )
    trees_saved = models.FloatField(
        default=0,
        help_text="Equivalent number of trees saved",
        blank=True,
        null=True
    )
    
    impact_type = models.CharField(
        max_length=20,
        choices=[
            ('product', 'Product'),
            ('recycling', 'Recycling'),
            ('other', 'Other')
        ],
        default='product'
    )
    
    def __str__(self):
        return f"EcoImpact for {self.user.username} on {self.date_recorded}"

class RecyclableItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=100, choices=[
        ('electronics', 'Electronics'),
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('other', 'Other')
    ])
    condition = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('used', 'Used'),
        ('damaged', 'Damaged'),
    ])
    image = models.ImageField(upload_to=product_image_upload_to, blank=True, null=True)
    pickup_scheduled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Recycling-specific impact estimates
    estimated_co2_saving = models.FloatField(
        default=0,
        help_text="Estimated CO2 savings from recycling (kg)",
        blank=True,
        null=True
    )
    estimated_water_saving = models.FloatField(
        default=0,
        help_text="Estimated water savings from recycling (liters)",
        blank=True,
        null=True
    )
    estimated_waste_reduction = models.FloatField(
        default=0,
        help_text="Estimated waste reduction from recycling (kg)",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.item_name
