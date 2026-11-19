from django.test import TestCase

# Create your tests here.
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Employee
from django.urls import reverse
from django.contrib.auth import get_user_model

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

class LandingPageTests(TestCase):
    def test_landing_page_loads(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_landing_page_has_login_button(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Login')

    def test_landing_page_is_responsive(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'name="viewport"')

class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = 'hruser'
        self.password = 'StrongPass123!'
        self.user = get_user_model().objects.create_user(
            username=self.username, password=self.password
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': self.password},
        )
        self.assertRedirects(response, reverse('dashboard'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': 'wrong-password'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('dashboard')}"
        )

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_logout_via_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_logout_via_get_not_allowed(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)