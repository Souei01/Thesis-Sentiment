import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete demo faculty accounts
maria = User.objects.filter(email='prof.maria.cruz@wmsu.edu.ph').first()
pedro = User.objects.filter(email='prof.pedro.reyes@wmsu.edu.ph').first()

deleted_count = 0

if maria:
    maria.delete()
    deleted_count += 1
    print('✓ Deleted Prof. Maria Cruz')
else:
    print('× Prof. Maria Cruz not found')

if pedro:
    pedro.delete()
    deleted_count += 1
    print('✓ Deleted Prof. Pedro Reyes')
else:
    print('× Prof. Pedro Reyes not found')

print(f'\nTotal accounts deleted: {deleted_count}')
