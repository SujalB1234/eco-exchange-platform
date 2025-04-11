# Generated by Django 5.1.6 on 2025-03-31 16:40

import accounts.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('for_sale', 'For Sale'), ('for_exchange', 'For Exchange'), ('for_donation', 'For Donation'), ('Recycling', 'For Recycling')], max_length=20)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=accounts.models.product_image_upload_to)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=50, null=True)),
                ('estimated_co2_saving', models.FloatField(blank=True, default=0, help_text='Estimated CO2 savings in kg', null=True)),
                ('estimated_water_saving', models.FloatField(blank=True, default=0, help_text='Estimated water savings in liters', null=True)),
                ('estimated_waste_reduction', models.FloatField(blank=True, default=0, help_text='Estimated waste reduction in kg', null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecyclableItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('item_type', models.CharField(choices=[('electronics', 'Electronics'), ('plastic', 'Plastic'), ('glass', 'Glass'), ('paper', 'Paper'), ('metal', 'Metal'), ('other', 'Other')], max_length=100)),
                ('condition', models.CharField(choices=[('new', 'New'), ('used', 'Used'), ('damaged', 'Damaged')], max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to=accounts.models.product_image_upload_to)),
                ('pickup_scheduled', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('estimated_co2_saving', models.FloatField(blank=True, default=0, help_text='Estimated CO2 savings from recycling (kg)', null=True)),
                ('estimated_water_saving', models.FloatField(blank=True, default=0, help_text='Estimated water savings from recycling (liters)', null=True)),
                ('estimated_waste_reduction', models.FloatField(blank=True, default=0, help_text='Estimated waste reduction from recycling (kg)', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EcoImpact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('co2_saved_kg', models.FloatField(default=0, help_text='CO2 saved in kilograms')),
                ('water_saved_liters', models.FloatField(default=0, help_text='Water saved in liters')),
                ('waste_diverted_kg', models.FloatField(default=0, help_text='Waste diverted from landfills in kg')),
                ('trees_saved', models.FloatField(blank=True, default=0, help_text='Equivalent number of trees saved', null=True)),
                ('impact_type', models.CharField(choices=[('product', 'Product'), ('recycling', 'Recycling'), ('other', 'Other')], default='product', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eco_impacts', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(blank=True, help_text='Associated product if impact is from a product', null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.product')),
                ('recyclable_item', models.ForeignKey(blank=True, help_text='Associated recyclable item if impact is from recycling', null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.recyclableitem')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('bio', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
