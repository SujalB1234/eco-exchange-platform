from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from .models import UserProfile, Product, Category, EcoImpact, RecyclableItem
from .forms import ProductForm, RecyclableItemForm

# ========== AUTHENTICATION VIEWS ==========
def signup_view(request):
    """Handle user registration with validation"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = []
        if not all([username, email, password, confirm_password]):
            errors.append("All fields are required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")
        if User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('signup')

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.create(user=user)
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Both fields are required.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# ========== PROFILE VIEWS ==========
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            request.user.first_name = request.POST.get('full-name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            if 'profile-pic' in request.FILES:
                profile.profile_picture = request.FILES['profile-pic']
            request.user.save()
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    
    return render(request, 'accounts/edit_profile.html', {'profile': profile})

# ========== PRODUCT VIEWS ==========
@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.user = request.user
                    
                    # Get the category object directly from the form
                    product.category = form.cleaned_data['category']
                    
                    # Set contact and location fields
                    product.contact_number = form.cleaned_data['contact_number']
                    product.location = form.cleaned_data['location']
                    
                    product.save()
                    
                    # Create EcoImpact record
                    EcoImpact.objects.create(
                        user=request.user,
                        product=product,
                        co2_saved_kg=product.estimated_co2_saving or 0,
                        water_saved_liters=product.estimated_water_saving or 0,
                        waste_diverted_kg=product.estimated_waste_reduction or 0,
                        impact_type='product'
                    )
                    
                    messages.success(request, "✅ Product added successfully!")
                    return redirect('product_listing')
            except Exception as e:
                messages.error(request, f"❌ Error saving product: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field.title()}: {error}")
    else:
        form = ProductForm(initial={'status': 'for_sale'})
    
    return render(request, 'accounts/add_product.html', {
        'form': form,
        'categories': Category.objects.all()
    })

def product_listing_view(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')

    products = Product.objects.select_related('category').all()
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if status:
        products = products.filter(status=status)

    return render(request, 'accounts/product_listing.html', {
        'products': products,
        'categories': Category.objects.all(),
        'status_choices': Product.STATUS_CHOICES,
    })

def product_detail_view(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category'), id=product_id)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'accounts/product_detail.html', {
        'product': product,
        'similar_products': similar_products,
        'show_contact': True
    })

@login_required
def confirm_delete_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "✅ Product deleted successfully!")
        return redirect('product_listing')
    return render(request, 'accounts/confirm_delete.html', {'product': product})

@login_required
def view_products(request, status):
    products = Product.objects.filter(status=status).select_related('category')
    return render(request, 'accounts/view_products.html', {
        'products': products,
        'status': status,
        'show_contact': True
    })

# ========== RECYCLING VIEWS ==========
@login_required
def add_recyclable_item(request):
    if request.method == 'POST':
        form = RecyclableItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.user = request.user
                    item.save()
                    
                    EcoImpact.objects.create(
                        user=request.user,
                        recyclable_item=item,
                        co2_saved_kg=item.estimated_co2_saving or 0,
                        water_saved_liters=item.estimated_water_saving or 0,
                        waste_diverted_kg=item.estimated_waste_reduction or 0,
                        impact_type='recycling'
                    )
                    
                    messages.success(request, "✅ Item added successfully!")
                    return redirect('recycling_dashboard')
            except Exception as e:
                messages.error(request, f"❌ Error saving item: {str(e)}")
    else:
        form = RecyclableItemForm()
    
    return render(request, 'accounts/add_recyclable_item.html', {'form': form})

# ========== DONATION VIEWS ==========
def donation_product_listing_view(request):
    products = Product.objects.filter(status='for_donation').select_related('category')
    return render(request, 'accounts/donation_product_listing.html', {
        'products': products,
    })

# ========== BASIC VIEWS ==========
def home_view(request):
    return render(request, 'accounts/home.html')

@login_required
def dashboard_view(request):
    products = Product.objects.filter(user=request.user).select_related('category')
    recyclable_items = RecyclableItem.objects.filter(user=request.user)
    
    total_impact = {
        'co2_saved': sum(
            p.estimated_co2_saving for p in products if p.estimated_co2_saving
        ) + sum(
            r.estimated_co2_saving for r in recyclable_items if r.estimated_co2_saving
        ),
        'water_saved': sum(
            p.estimated_water_saving for p in products if p.estimated_water_saving
        ) + sum(
            r.estimated_water_saving for r in recyclable_items if r.estimated_water_saving
        ),
        'waste_reduced': sum(
            p.estimated_waste_reduction for p in products if p.estimated_waste_reduction
        ) + sum(
            r.estimated_waste_reduction for r in recyclable_items if r.estimated_waste_reduction
        )
    }
    
    return render(request, 'accounts/dashboard.html', {
        'product_count': products.count(),
        'products_for_sale': products.filter(status='for_sale').count(),
        'products_for_exchange': products.filter(status='for_exchange').count(),
        'recyclable_items_count': recyclable_items.count(),
        'total_impact': total_impact
    })

# ========== USER DASHBOARD ==========

def user_dashboard(request):
    """Dashboard showing user's eco impact statistics"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Show a public version of the dashboard or redirect
        return render(request, 'accounts/user_dashboard.html', {
            'public_mode': True,
            'total_co2_saved': 0,
            'total_water_saved': 0,
            'total_waste_diverted': 0
        })
    
    eco_impact = EcoImpact.objects.filter(user=request.user)
    
    # Summing up all impact values
    total_co2_saved = sum(impact.co2_saved_kg for impact in eco_impact)
    total_water_saved = sum(impact.water_saved_liters for impact in eco_impact)
    total_waste_diverted = sum(impact.waste_diverted_kg for impact in eco_impact)

    context = {
        'public_mode': False,
        'total_co2_saved': total_co2_saved,
        'total_water_saved': total_water_saved,
        'total_waste_diverted': total_waste_diverted,
    }
    return render(request, 'accounts/user_dashboard.html', context)