import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Update CS Department Head
cs_head = User.objects.filter(email='cs.head@wmsu.edu.ph').first()
if cs_head:
    cs_head.role = 'admin'
    cs_head.admin_subrole = 'dept_head_cs'
    cs_head.department = 'CS'
    cs_head.save()
    print(f'✓ Updated CS Department Head: {cs_head.email}')
    print(f'  Role: {cs_head.role}, Subrole: {cs_head.admin_subrole}, Department: {cs_head.department}')
else:
    print('× CS Department Head not found')

# Update IT Department Head
it_head = User.objects.filter(email='it.head@wmsu.edu.ph').first()
if it_head:
    it_head.role = 'admin'
    it_head.admin_subrole = 'dept_head_it'
    it_head.department = 'IT'
    it_head.save()
    print(f'\n✓ Updated IT Department Head: {it_head.email}')
    print(f'  Role: {it_head.role}, Subrole: {it_head.admin_subrole}, Department: {it_head.department}')
else:
    print('× IT Department Head not found')

print('\nDepartment heads configured successfully!')
