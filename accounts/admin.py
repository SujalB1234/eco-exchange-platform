from django.contrib import admin
from .models import Product, Category, EcoImpact, UserProfile, RecyclableItem

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

# Register all models
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(EcoImpact)
admin.site.register(UserProfile)
admin.site.register(RecyclableItem)