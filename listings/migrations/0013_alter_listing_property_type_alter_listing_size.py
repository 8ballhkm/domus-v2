# Generated by Django 5.2.1 on 2025-06-02 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0012_delete_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='property_type',
            field=models.CharField(choices=[('House', 'House'), ('Apartment', 'Apartment'), ('Commercial', 'Commercial'), ('Land', 'Land'), ('Condo', 'Condo'), ('Penthouse', 'Penthouse')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='listing',
            name='size',
            field=models.CharField(choices=[('None', 'None'), ('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large'), ('Master', 'Master')], default='', max_length=50),
        ),
    ]
