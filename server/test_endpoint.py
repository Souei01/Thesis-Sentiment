"""
Test the response stats endpoint directly
Run in Render shell: python test_endpoint.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.test import RequestFactory
from api.views import get_response_stats
from authentication.models import User
import json

print("=== Testing Response Stats Endpoint ===\n")

# Get a faculty user
faculty = User.objects.filter(role='faculty').first()
if not faculty:
    print("ERROR: No faculty found")
    exit(1)

print(f"Testing as: {faculty.email} ({faculty.role})")

# Create a fake request
factory = RequestFactory()
request = factory.get('/api/feedback/response-stats/')
request.user = faculty

print("\nCalling get_response_stats()...")

try:
    response = get_response_stats(request)
    print(f"\n✓ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"\nResponse data:")
        print(f"  Total Students: {data.get('total_students')}")
        print(f"  Total Responses: {data.get('total_responses')}")
        print(f"  Response Rate: {data.get('response_rate')}")
        print(f"  Respondents: {len(data.get('respondents', []))}")
        print(f"  Non-Respondents: {len(data.get('non_respondents', []))}")
    else:
        print(f"\n✗ Error response:")
        print(response.content.decode('utf-8'))
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    
    import traceback
    print(f"\n   Full traceback:")
    traceback.print_exc()

print("\n=== Test Complete ===")
