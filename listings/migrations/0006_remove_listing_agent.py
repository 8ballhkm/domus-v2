# Generated by Django 5.2 on 2025-05-21 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0005_remove_listing_image_listing_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='agent',
        ),
    ]
