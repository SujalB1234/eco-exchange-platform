import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------------- Utilities ----------------------
def product_image_upload_to(instance, filename):
    """Generate dynamic upload path for product images."""
    base_filename, file_extension = os.path.splitext(filename)
    return f'product_images/{instance.name}/{base_filename}_{instance.id}{file_extension}'

# ---------------------- User Profile ----------------------
class UserProfile(models.Model):
    """Extended user profile storing eco-related data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    items_shared = models.PositiveIntegerField(default=0)
    items_recycled = models.PositiveIntegerField(default=0)
    total_co2_saved = models.FloatField(default=0)
    total_water_saved = models.FloatField(default=0)
    total_waste_reduced = models.FloatField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'

    def update_eco_stats(self):
        """Update all eco-impact statistics from related products and recyclables."""
        from django.db.models import Sum

        product_stats = Product.objects.filter(user=self.user).aggregate(
            total_co2=Sum('estimated_co2_saving'),
            total_water=Sum('estimated_water_saving'),
            total_waste=Sum('estimated_waste_reduction')
        )

        recycle_stats = RecyclableItem.objects.filter(user=self.user).aggregate(
            total_co2=Sum('estimated_co2_saving'),
            total_water=Sum('estimated_water_saving'),
            total_waste=Sum('estimated_waste_reduction')
        )

        self.items_shared = Product.objects.filter(user=self.user).count()
        self.items_recycled = RecyclableItem.objects.filter(user=self.user).count()
        self.total_co2_saved = (product_stats['total_co2'] or 0) + (recycle_stats['total_co2'] or 0)
        self.total_water_saved = (product_stats['total_water'] or 0) + (recycle_stats['total_water'] or 0)
        self.total_waste_reduced = (product_stats['total_waste'] or 0) + (recycle_stats['total_waste'] or 0)
        self.save()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Automatically create or update a UserProfile on user save."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

# ---------------------- Category ----------------------
class Category(models.Model):
    """Categories for product classification."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# ---------------------- Product ----------------------
class Product(models.Model):
    """Products shared for sale, donation, exchange, or recycling."""
    STATUS_CHOICES = [
        ('for_sale', 'For Sale'),
        ('for_exchange', 'For Exchange'),
        ('for_donation', 'For Donation'),
        ('recycling', 'For Recycling'),
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    estimated_co2_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_water_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_waste_reduction = models.FloatField(default=0, blank=True, null=True)

    recycle_worker = models.ForeignKey('RecycleWorker', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.user, 'userprofile'):
            self.user.userprofile.update_eco_stats()

# ---------------------- Recyclable Item ----------------------
class RecyclableItem(models.Model):
    """Recyclable items submitted by users."""
    ITEM_TYPE_CHOICES = [
        ('electronics', 'Electronics'),
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('textile', 'Textile'),
        ('other', 'Other'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('worn', 'Worn'),
        ('damaged', 'Damaged'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES)
    condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, default='good')
    image = models.ImageField(upload_to='recyclable_items/', blank=True, null=True)

    estimated_co2_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_water_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_waste_reduction = models.FloatField(default=0, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.user, 'userprofile'):
            self.user.userprofile.update_eco_stats()

# ---------------------- Recycle Worker ----------------------
class RecycleWorker(models.Model):
    """Recycling staff assigned to handle recyclable products."""
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    specialization = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# ---------------------- Eco Impact ----------------------
class EcoImpact(models.Model):
    """Tracks environmental impact data."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eco_impacts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    recyclable_item = models.ForeignKey(RecyclableItem, on_delete=models.CASCADE, null=True, blank=True)

    date_recorded = models.DateTimeField(auto_now_add=True)
    co2_saved_kg = models.FloatField(default=0)
    water_saved_liters = models.FloatField(default=0)
    waste_diverted_kg = models.FloatField(default=0)
    trees_saved = models.FloatField(default=0, blank=True, null=True)

    impact_type = models.CharField(
        max_length=20,
        choices=[
            ('product', 'Product'),
            ('recycling', 'Recycling'),
            ('other', 'Other'),
        ],
        default='product'
    )

    def __str__(self):
        return f"EcoImpact for {self.user.username} on {self.date_recorded}"
