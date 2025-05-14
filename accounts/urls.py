from django.urls import path
from . import views
from .views import assign_worker_list_view
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('product_listing/', views.product_listing_view, name='product_listing'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('confirm_delete/<int:product_id>/', views.confirm_delete_view, name='confirm_delete'),
    path('view_products/<str:status>/', views.view_products, name='view_products'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-products/', views.my_products_view, name='my_products'),

    
    # Add the URL for the user's product list
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    
    # Add the URL for donation information
     path('donations/', views.donation_product_listing_view, name='donation_listing'),
     path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    path('recycle-workers/', views.recycle_worker_list, name='recycle_worker_list'),
    path('admin/assign-worker/', assign_worker_list_view, name='admin_assign_worker_list'),
    path('assign-worker/<int:product_id>/', views.assign_recycle_worker, name='assign_recycle_worker'),
    path('recycle-worker/dashboard/', views.recycle_worker_dashboard, name='recycle_worker_dashboard'),
    path('recycle-worker/login/', views.recycle_worker_login, name='recycle_worker_login'),
    path('admin/worker-dashboard/', views.admin_worker_dashboard, name='admin_worker_dashboard'),
    path('recycle-worker/logout/', views.recycle_worker_logout, name='recycle_worker_logout'),


  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]