import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------------- Utilities ----------------------
def product_image_upload_to(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'product_images/{instance.name}/{base_filename}_{instance.id}{file_extension}'

# ---------------------- User Profile ----------------------
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile',
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True, default='')
    items_shared = models.PositiveIntegerField(default=0)
    items_recycled = models.PositiveIntegerField(default=0)
    total_co2_saved = models.FloatField(default=0)
    total_water_saved = models.FloatField(default=0)
    total_waste_reduced = models.FloatField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'

    def update_eco_stats(self):
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
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()

# ---------------------- Category ----------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# ---------------------- Product ----------------------
class Product(models.Model):
    STATUS_CHOICES = [
        ('for_sale', 'For Sale'),
        ('for_exchange', 'For Exchange'),
        ('for_donation', 'For Donation'),
        ('recycling', 'For Recycling'),
    ]

    RECYCLE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    recycle_status = models.CharField(choices=RECYCLE_STATUS_CHOICES, max_length=20, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    estimated_co2_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_water_saving = models.FloatField(default=0, blank=True, null=True)
    estimated_waste_reduction = models.FloatField(default=0, blank=True, null=True)

    recycle_worker = models.ForeignKey('RecycleWorker', null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    pickup_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.user, 'userprofile'):
            self.user.userprofile.update_eco_stats()
        if self.recycle_status == 'assigned' and self.pickup_time:
            self.send_pickup_notification()

    def send_pickup_notification(self):
        from .models import Notification
        message = f"A recycle worker has been assigned to collect your product: {self.name}. The pickup is scheduled for {self.pickup_time.strftime('%Y-%m-%d %H:%M')}."
        Notification.objects.create(
            user=self.user,
            message=message,
            is_read=False
        )

# ---------------------- Recyclable Item ----------------------
class RecyclableItem(models.Model):
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

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('collected', 'Collected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES)
    condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, default='good')
    image = models.ImageField(upload_to='recyclable_items/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_worker = models.ForeignKey('RecycleWorker', on_delete=models.SET_NULL, null=True, blank=True, related_name='recyclable_items')

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    specialization = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# ---------------------- Eco Impact ----------------------
class EcoImpact(models.Model):
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

# ---------------------- Notification ----------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To: {self.user.username} - {self.message[:30]}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
