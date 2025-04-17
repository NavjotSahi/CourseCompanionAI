# backend/api/models.py
from django.db import models
from django.contrib.auth.models import User # Use Django's built-in User model for now

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='taught_courses') # Link to a user acting as teacher

    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students_enrolled')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course') # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.code}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    total_points = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.title} ({self.course.code})"

class Grade(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # e.g., 85.50
    submission_status = models.CharField(max_length=20, default='Pending') # e.g., Pending, Submitted, Graded, Late
    submitted_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assignment', 'student') # One grade per student per assignment

    def __str__(self):
        return f"Grade for {self.student.username} on {self.assignment.title}"

# Add models for Course Content later (e.g., linking files to Courses)