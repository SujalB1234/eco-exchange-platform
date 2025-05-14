from django import forms
from .models import Product, Category, RecyclableItem, RecycleWorker
from .models import ContactMessage

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'status', 
                  'image', 'contact_number', 'location',
                  'estimated_co2_saving', 'estimated_water_saving', 
                  'estimated_waste_reduction']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_co2_saving': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_water_saving': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_waste_reduction': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RecyclableItemForm(forms.ModelForm):
    class Meta:
        model = RecyclableItem
        fields = ['item_name', 'description', 'item_type', 'condition', 'image',
                  'estimated_co2_saving', 'estimated_water_saving', 
                  'estimated_waste_reduction']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'estimated_co2_saving': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_water_saving': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_waste_reduction': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AssignRecycleWorkerForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(status='Pending'),
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    recycle_worker = forms.ModelChoiceField(
        queryset=RecycleWorker.objects.all(),
        label="Select Recycle Worker",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']