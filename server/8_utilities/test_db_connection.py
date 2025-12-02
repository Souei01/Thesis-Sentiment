"""
Test database connection and show current settings
"""

import os
import django

# Set environment variables for MariaDB
os.environ['DB_ENGINE'] = 'mysql'
os.environ['DB_NAME'] = 'sentiment_db'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_PORT'] = '3306'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.db import connection
from django.conf import settings

print("=" * 80)
print("DATABASE CONNECTION TEST")
print("=" * 80)

# Show current database configuration
db_config = settings.DATABASES['default']
print("\n📊 Current Database Configuration:")
print("-" * 80)
print(f"Engine:   {db_config['ENGINE']}")
print(f"Name:     {db_config['NAME']}")
print(f"User:     {db_config['USER']}")
print(f"Password: {'(empty)' if not db_config['PASSWORD'] else '(set)'}")
print(f"Host:     {db_config['HOST']}")
print(f"Port:     {db_config['PORT']}")

# Test connection
print("\n" + "=" * 80)
print("Testing Connection...")
print("-" * 80)

try:
    # Try to get database cursor
    with connection.cursor() as cursor:
        # Execute a simple query
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"   Database Version: {version}")
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, [db_config['NAME']])
        table_count = cursor.fetchone()[0]
        print(f"   Tables in database: {table_count}")
        
        # List some tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            ORDER BY table_name
        """, [db_config['NAME']])
        tables = cursor.fetchall()
        print(f"\n   Tables:")
        for table in tables[:10]:  # Show first 10 tables
            print(f"      - {table[0]}")
        if len(tables) > 10:
            print(f"      ... and {len(tables) - 10} more")
            
except Exception as e:
    print(f"❌ Connection failed!")
    print(f"   Error: {e}")
    print(f"\n💡 Make sure:")
    print(f"   1. XAMPP MySQL/MariaDB is running")
    print(f"   2. Database 'sentiment_db' exists")
    print(f"   3. User 'root' has access to the database")

print("\n" + "=" * 80)
print("Environment Variables:")
print("-" * 80)
print(f"DB_ENGINE:   {os.environ.get('DB_ENGINE', '(not set)')}")
print(f"DB_NAME:     {os.environ.get('DB_NAME', '(not set)')}")
print(f"DB_USER:     {os.environ.get('DB_USER', '(not set)')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', '(not set)')}")
print(f"DB_HOST:     {os.environ.get('DB_HOST', '(not set)')}")
print(f"DB_PORT:     {os.environ.get('DB_PORT', '(not set)')}")
print("=" * 80)
