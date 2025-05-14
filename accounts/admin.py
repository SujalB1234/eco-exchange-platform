from django.contrib import admin
from .models import Product, Category, EcoImpact, UserProfile, RecyclableItem, RecycleWorker, ContactMessage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'price', 'user', 'contact_number', 'location')
    list_filter = ('status', 'category', 'user')
    search_fields = ('name', 'description', 'contact_number')
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'user')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'status')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'location')
        }),
        ('Eco Impact Metrics', {
            'fields': ('estimated_co2_saving', 'estimated_water_saving', 'estimated_waste_reduction'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Automatically set the user when creating a new product"""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(EcoImpact)
admin.site.register(UserProfile)
admin.site.register(RecyclableItem)
admin.site.register(RecycleWorker)

# Register ContactMessage model to the admin site
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submitted_at')  # Changed 'created_at' to 'submitted_at'
    search_fields = ('name', 'email', 'message')
    list_filter = ('submitted_at',)  # Changed 'created_at' to 'submitted_at'
    list_per_page = 20

admin.site.register(ContactMessage, ContactMessageAdmin)
