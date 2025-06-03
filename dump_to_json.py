import sys
from django.core.management import call_command

with open('data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata',
                 '--natural-primary',
                 '--natural-foreign',
                 '--exclude', 'auth.permission',
                 '--exclude', 'contenttypes',
                 stdout=f)
