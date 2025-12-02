from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'admin_subrole', 'year_level', 'section', 'department', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'admin_subrole', 'year_level', 'section', 'department', 'is_active', 'is_staff', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'student_id', 'department')}),
        ('Student Info', {'fields': ('year_level', 'section'), 'description': 'For students only - used for auto-enrollment'}),
        ('Admin Info', {'fields': ('role', 'admin_subrole')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'admin_subrole', 'year_level', 'section', 'department', 'password1', 'password2'),
        }),
    )
