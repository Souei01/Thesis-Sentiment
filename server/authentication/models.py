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
    
    def get_display_name(self):
        """Get a user-friendly display name for faculty"""
        if self.role == 'faculty':
            # Extract faculty identifier from email (e.g., facultyCS1 -> CSprofessor-1)
            email_prefix = self.email.split('@')[0]  # Get facultyCS1 from facultyCS1@wmsu.edu.ph
            
            # Check if it matches the pattern facultyXX# where XX is dept and # is number
            if email_prefix.startswith('faculty'):
                dept_and_num = email_prefix.replace('faculty', '')  # CS1, IT2, ICT3
                
                # Extract department code (letters) and number (digits)
                dept_code = ''.join([c for c in dept_and_num if c.isalpha()])  # CS, IT, ICT
                prof_num = ''.join([c for c in dept_and_num if c.isdigit()])   # 1, 2, 3
                
                if dept_code and prof_num:
                    return f"{dept_code}professor-{prof_num}"
            
            # Fallback: use first/last name or email
            if self.first_name and self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.email.split('@')[0]
        
        # For non-faculty, use full name or email
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def __str__(self):
        if self.role == 'admin' and self.admin_subrole:
            return f"{self.email} ({self.get_admin_subrole_display()})"
        return f"{self.email} ({self.get_role_display()})"
