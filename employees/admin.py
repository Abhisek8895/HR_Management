from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'department', 'designation', 'salary', 'joining_date')
    list_filter = ('department', 'joining_date')
    search_fields = ('name', 'email', 'designation')