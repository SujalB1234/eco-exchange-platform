# Generated by Django 5.1.6 on 2025-04-23 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_recycleworker_notes_alter_product_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recycleworker',
            name='notes',
        ),
    ]
