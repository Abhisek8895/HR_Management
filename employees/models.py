from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message='Enter a valid phone number (10-15 digits, optional leading +).',
)


class Employee(models.Model):
    class Department(models.TextChoices):
        HR = 'HR', 'Human Resources'
        IT = 'IT', 'Information Technology'
        FINANCE = 'FIN', 'Finance'
        MARKETING = 'MKT', 'Marketing'
        SALES = 'SALES', 'Sales'
        OPERATIONS = 'OPS', 'Operations'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        error_messages={'unique': 'An employee with this email already exists.'},
    )
    phone_number = models.CharField(max_length=16, validators=[phone_validator])
    department = models.CharField(max_length=10, choices=Department.choices)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    joining_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.designation})'

    def clean(self):
        super().clean()
        # Normalise before the unique check so duplicates are case-insensitive.
        if self.email:
            self.email = self.email.strip().lower()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)