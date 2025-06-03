import os
import django
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'domus.settings')  # Replace 'domus' with your project name
django.setup()

# Dump data to JSON
with open('data.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        '--natural-primary',
        '--natural-foreign',
        '--exclude', 'auth.permission',
        '--exclude', 'contenttypes',
        stdout=f
    )
