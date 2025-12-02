"""
Run all setup commands for deployment
Usage: python manage.py setup_deployment
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run all deployment setup commands'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('DEPLOYMENT SETUP')
        self.stdout.write('=' * 70)
        
        # Run migrations
        self.stdout.write('\n1. Running migrations...')
        call_command('migrate')
        
        # Create admin users
        self.stdout.write('\n2. Creating admin users...')
        try:
            call_command('seed_admin_users')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Admin users: {e}'))
        
        # Create regular users
        self.stdout.write('\n3. Creating regular users...')
        try:
            call_command('seed_users')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Regular users: {e}'))
        
        # Load production data
        self.stdout.write('\n4. Loading production data...')
        try:
            call_command('seed_production_data')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Production data: {e}'))
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ DEPLOYMENT SETUP COMPLETE'))
        self.stdout.write('=' * 70)
