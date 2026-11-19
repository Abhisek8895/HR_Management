from django.test import TestCase

# Create your tests here.
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Employee


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.data = {
            'name': 'Asha Verma',
            'email': 'asha@example.com',
            'phone_number': '9876543210',
            'department': Employee.Department.IT,
            'designation': 'Developer',
            'salary': Decimal('55000.00'),
            'joining_date': date(2024, 1, 15),
        }

    def test_create_employee(self):
        emp = Employee.objects.create(**self.data)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(str(emp), 'Asha Verma (Developer)')

    def test_email_is_lowercased_on_save(self):
        emp = Employee.objects.create(**{**self.data, 'email': 'ASHA@Example.com'})
        self.assertEqual(emp.email, 'asha@example.com')

    def test_duplicate_email_rejected_by_database(self):
        Employee.objects.create(**self.data)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Employee.objects.create(**self.data)

    def test_duplicate_email_case_insensitive_validation(self):
        Employee.objects.create(**self.data)
        dup = Employee(**{**self.data, 'email': 'ASHA@EXAMPLE.COM'})
        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_invalid_phone_rejected(self):
        emp = Employee(**{**self.data, 'phone_number': 'abc123'})
        with self.assertRaises(ValidationError) as ctx:
            emp.full_clean()
        self.assertIn('phone_number', ctx.exception.message_dict)

    def test_zero_or_negative_salary_rejected(self):
        for bad in (Decimal('0'), Decimal('-100')):
            emp = Employee(**{**self.data, 'salary': bad})
            with self.assertRaises(ValidationError) as ctx:
                emp.full_clean()
            self.assertIn('salary', ctx.exception.message_dict)

    def test_invalid_department_rejected(self):
        emp = Employee(**{**self.data, 'department': 'XYZ'})
        with self.assertRaises(ValidationError):
            emp.full_clean()