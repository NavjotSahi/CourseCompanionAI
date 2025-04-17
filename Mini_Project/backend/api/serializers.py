# backend/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Enrollment, Assignment, Grade

# Basic serializer for User info (read-only)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email'] # Fields you want to expose

# Serializer for Course model
class CourseSerializer(serializers.ModelSerializer):
    # teacher = UserSerializer(read_only=True) # Optionally nest teacher details
    teacher_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='teacher', write_only=True, required=False, allow_null=True) # For assigning teacher
    teacher_username = serializers.CharField(source='teacher.username', read_only=True) # Show username on read

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'teacher_id', 'teacher_username']

# Serializer for Assignment model
class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True) # Show course code

    class Meta:
        model = Assignment
        # Make course selectable by ID when creating/updating, but show code on read
        fields = ['id', 'course', 'course_code', 'title', 'description', 'due_date', 'total_points']
        read_only_fields = ['course_code'] # course_code is derived
        extra_kwargs = {
            'course': {'write_only': True} # Only use course ID for writing
        }

# Serializer for Grade model
class GradeSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    course_code = serializers.CharField(source='assignment.course.code', read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id',
            'assignment', # ID for writing
            'student',    # ID for writing
            'assignment_title',
            'student_username',
            'course_code',
            'score',
            'submission_status',
            'submitted_at',
            'feedback'
            ]
        read_only_fields = ['student_username', 'assignment_title', 'course_code']
        extra_kwargs = {
            'assignment': {'write_only': True},
            'student': {'write_only': True} # Usually set automatically based on logged-in user
        }

# Serializer specifically for listing courses a student is enrolled in
class StudentEnrollmentSerializer(serializers.ModelSerializer):
    # Nest the full course details within the enrollment info
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrollment_date']