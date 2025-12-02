"""
Create an active feedback session for testing
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import FeedbackSession

# Delete old sessions
FeedbackSession.objects.all().delete()

# Create new active session
start_date = datetime.now()
end_date = start_date + timedelta(days=30)  # Active for 30 days

session = FeedbackSession.objects.create(
    title='1st Semester 2024-2025 Feedback',
    start_date=start_date,
    end_date=end_date,
    semester='1st',
    academic_year='2024-2025',
    is_active=True,
    instructions='Please provide honest feedback about your courses.'
)

print(f"✅ Created feedback session: {session.title}")
print(f"   Start: {session.start_date}")
print(f"   End: {session.end_date}")
print(f"   Active: {session.is_active}")
