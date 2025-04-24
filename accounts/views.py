from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.conf import settings
import os
from .models import UserProfile, Product, Category, EcoImpact, RecyclableItem
from .forms import ProductForm, RecyclableItemForm
from .models import RecycleWorker
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AssignRecycleWorkerForm

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
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                # Create user profile with default picture
                profile = UserProfile.objects.create(user=user)
                
                # Set default profile picture
                default_pic_path = os.path.join(settings.STATIC_ROOT, 'images/default_profile.png')
                if os.path.exists(default_pic_path):
                    with open(default_pic_path, 'rb') as f:
                        profile.profile_picture.save(
                            f'default_{user.id}.png',
                            f,
                            save=True
                        )
                
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('signup')
    
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
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """Handle user logout"""
    username = request.user.username
    logout(request)
    messages.success(request, f"You have been logged out, {username}. Come back soon!")
    return redirect('login')

# ========== PROFILE VIEWS ==========
@login_required
def profile_view(request):
    """Display user profile with proper image handling"""
    try:
        profile = UserProfile.objects.select_related('user').get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # Calculate eco impact stats
    eco_stats = EcoImpact.objects.filter(user=request.user).aggregate(
        total_co2=Sum('co2_saved_kg'),
        total_water=Sum('water_saved_liters'),
        total_waste=Sum('waste_diverted_kg')
    )
    
    context = {
        'profile': profile,
        'user': request.user,
        'total_co2_saved': eco_stats['total_co2'] or 0,
        'total_water_saved': eco_stats['total_water'] or 0,
        'total_waste_reduced': eco_stats['total_waste'] or 0
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    """Edit user profile with robust file handling"""
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update user fields
                user = request.user
                user.first_name = request.POST.get('full_name', '').strip()
                user.email = request.POST.get('email', '').strip()
                
                # Update profile fields
                profile.bio = request.POST.get('bio', '').strip()
                
                # Handle profile picture changes
                if 'profile_picture' in request.FILES:
                    # Delete old picture if exists
                    if profile.profile_picture:
                        profile.profile_picture.delete(save=False)
                    # Save new picture
                    profile.profile_picture = request.FILES['profile_picture']
                
                # Handle picture removal
                if request.POST.get('remove_picture') == 'true':
                    if profile.profile_picture:
                        profile.profile_picture.delete(save=False)
                    profile.profile_picture = None
                
                user.save()
                profile.save()
                
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
                
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            return redirect('edit_profile')
    
    return render(request, 'accounts/edit_profile.html', {
        'profile': profile,
        'user': request.user
    })

# ========== PRODUCT VIEWS ==========
@login_required
def add_product_view(request):
    """Add new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.user = request.user
                    product.category = form.cleaned_data['category']
                    product.contact_number = form.cleaned_data['contact_number']
                    product.location = form.cleaned_data['location']
                    product.save()
                    
                    # Update user stats
                    profile = request.user.userprofile
                    profile.items_shared = Product.objects.filter(user=request.user).count()
                    profile.save()
                    
                    # Create eco impact record
                    EcoImpact.objects.create(
                        user=request.user,
                        product=product,
                        co2_saved_kg=product.estimated_co2_saving or 0,
                        water_saved_liters=product.estimated_water_saving or 0,
                        waste_diverted_kg=product.estimated_waste_reduction or 0,
                        impact_type='product'
                    )
                    
                    messages.success(request, "Product added successfully!")
                    return redirect('product_listing')
            except Exception as e:
                messages.error(request, f"Error saving product: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = ProductForm(initial={'status': 'for_sale'})
    
    return render(request, 'accounts/add_product.html', {
        'form': form,
        'categories': Category.objects.all()
    })

def product_listing_view(request):
    """List all products with filters"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')

    products = Product.objects.select_related('category', 'user').all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
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
    """Product detail view"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'user'),
        id=product_id
    )
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    return render(request, 'accounts/product_detail.html', {
        'product': product,
        'similar_products': similar_products,
        'show_contact': True
    })

def confirm_delete_view(request, product_id):
    """Confirm product deletion"""
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        product.delete()
        # Update user stats
        profile = request.user.userprofile
        profile.items_shared = Product.objects.filter(user=request.user).count()
        profile.save()
        messages.success(request, "Product deleted successfully!")
        return redirect('product_listing')
        
    return render(request, 'accounts/confirm_delete.html', {'product': product})


def view_products(request, status):
    """View products by status"""
    products = Product.objects.filter(
        status=status
    ).select_related('category', 'user')
    
    return render(request, 'accounts/view_products.html', {
        'products': products,
        'status': status,
        'show_contact': True
    })

# ========== RECYCLING VIEWS ==========
def add_recyclable_item(request):
    """Add recyclable item"""
    if request.method == 'POST':
        form = RecyclableItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.user = request.user
                    item.save()
                    
                    # Update user stats
                    profile = request.user.userprofile
                    profile.items_recycled = RecyclableItem.objects.filter(
                        user=request.user
                    ).count()
                    profile.save()
                    
                    # Create eco impact record
                    EcoImpact.objects.create(
                        user=request.user,
                        recyclable_item=item,
                        co2_saved_kg=item.estimated_co2_saving or 0,
                        water_saved_liters=item.estimated_water_saving or 0,
                        waste_diverted_kg=item.estimated_waste_reduction or 0,
                        impact_type='recycling'
                    )
                    
                    messages.success(request, "Item added successfully!")
                    return redirect('recycling_dashboard')
            except Exception as e:
                messages.error(request, f"Error saving item: {str(e)}")
    else:
        form = RecyclableItemForm()
    
    return render(request, 'accounts/add_recyclable_item.html', {'form': form})

# ========== DONATION VIEWS ==========
def donation_product_listing_view(request):
    """List donation products"""
    products = Product.objects.filter(
        status='for_donation'
    ).select_related('category', 'user')
    
    return render(request, 'accounts/donation_product_listing.html', {
        'products': products,
    })

# ========== BASIC VIEWS ==========
def home_view(request):
    """Home page view"""
    context = {
        'username': None,
        'items_shared': 0,
        'items_recycled': 0,
        'total_co2_saved': 0,
        'total_water_saved': 0,
        'total_waste_reduced': 0,
    }

    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            eco_stats = EcoImpact.objects.filter(user=request.user).aggregate(
                total_co2=Sum('co2_saved_kg'),
                total_water=Sum('water_saved_liters'),
                total_waste=Sum('waste_diverted_kg')
            )
            
            context.update({
                'username': request.user.get_full_name() or request.user.username,
                'items_shared': profile.items_shared,
                'items_recycled': profile.items_recycled,
                'total_co2_saved': eco_stats['total_co2'] or 0,
                'total_water_saved': eco_stats['total_water'] or 0,
                'total_waste_reduced': eco_stats['total_waste'] or 0,
            })
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
            context['username'] = request.user.username
    
    return render(request, 'accounts/home.html', context)

@login_required
def dashboard_view(request):
    """User dashboard"""
    profile = request.user.userprofile
    products = Product.objects.filter(user=request.user).select_related('category')
    recyclable_items = RecyclableItem.objects.filter(user=request.user)
    
    # Calculate total impacts
    total_impacts = EcoImpact.objects.filter(user=request.user).aggregate(
        co2_saved=Sum('co2_saved_kg'),
        water_saved=Sum('water_saved_liters'),
        waste_reduced=Sum('waste_diverted_kg')
    )
    
    return render(request, 'accounts/dashboard.html', {
        'product_count': products.count(),
        'products_for_sale': products.filter(status='for_sale').count(),
        'products_for_exchange': products.filter(status='for_exchange').count(),
        'recyclable_items_count': recyclable_items.count(),
        'total_impact': {
            'co2_saved': total_impacts['co2_saved'] or 0,
            'water_saved': total_impacts['water_saved'] or 0,
            'waste_reduced': total_impacts['waste_reduced'] or 0
        }
    })

# ========== USER DASHBOARD ==========
def user_dashboard(request):
    """Public user dashboard showing eco impact"""
    if not request.user.is_authenticated:
        return render(request, 'accounts/user_dashboard.html', {
            'public_mode': True,
            'total_co2_saved': 0,
            'total_water_saved': 0,
            'total_waste_diverted': 0
        })
    
    profile = request.user.userprofile
    total_impacts = EcoImpact.objects.filter(user=request.user).aggregate(
        co2_saved=Sum('co2_saved_kg'),
        water_saved=Sum('water_saved_liters'),
        waste_reduced=Sum('waste_diverted_kg')
    )
    
    context = {
        'public_mode': False,
        'total_co2_saved': total_impacts['co2_saved'] or 0,
        'total_water_saved': total_impacts['water_saved'] or 0,
        'total_waste_diverted': total_impacts['waste_reduced'] or 0,
        'items_shared': profile.items_shared,
        'items_recycled': profile.items_recycled,
    }
    return render(request, 'accounts/user_dashboard.html', context)


@login_required
def my_products_view(request):
    my_products = Product.objects.filter(user=request.user)
    return render(request, 'accounts/my_products.html', {'products': my_products})


def recycle_worker_list(request):
    workers = RecycleWorker.objects.all()
    return render(request, 'accounts/recycle_worker_list.html', {'workers': workers})


@staff_member_required
def admin_assign_worker_list(request):
    products = Product.objects.filter(recycle_worker__isnull=True)
    return render(request, 'accounts/assign_worker_list.html', {'products': products})

@staff_member_required
def assign_recycle_worker(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    workers = RecycleWorker.objects.filter(available=True)

    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        if worker_id:
            worker = get_object_or_404(RecycleWorker, id=worker_id)
            product.recycle_worker = worker
            product.save()
            return redirect('admin_assign_worker_list')

    return render(request, 'accounts/assign_worker_form.html', {
        'product': product,
        'workers': workers
    })
