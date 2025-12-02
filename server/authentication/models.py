from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]

    # Admin subroles: two department heads (CS and IT) and one dean
    ADMIN_SUBROLE_CHOICES = [
        ('dept_head_cs', 'CS Department Head'),
        ('dept_head_it', 'IT Department Head'),
        ('dean', 'Dean'),
    ]
    
    YEAR_LEVEL_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    # When role == 'admin', admin_subrole can be set to specify which admin
    admin_subrole = models.CharField(max_length=30, choices=ADMIN_SUBROLE_CHOICES, blank=True, null=True)

    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Student-specific fields for auto-enrollment
    year_level = models.IntegerField(
        choices=YEAR_LEVEL_CHOICES,
        blank=True,
        null=True,
        help_text="For students only - used for auto-enrollment"
    )
    section = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="For students only (e.g., 3A, 2B) - used for auto-enrollment"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        if self.role == 'admin' and self.admin_subrole:
            return f"{self.email} ({self.get_admin_subrole_display()})"
        return f"{self.email} ({self.get_role_display()})"
