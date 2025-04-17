# backend/api/admin.py
from django.contrib import admin
from .models import Course, Enrollment, Assignment, Grade

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Grade)