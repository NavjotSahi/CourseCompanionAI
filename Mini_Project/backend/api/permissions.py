# backend/api/permissions.py
from rest_framework import permissions

def _is_in_group(user, group_name):
    """Checks if the user is in the specified group."""
    return user.groups.filter(name=group_name).exists()

class IsTeacher(permissions.BasePermission):
    """Allows access only to users in the 'Teachers' group."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _is_in_group(request.user, 'Teachers')

class IsStudent(permissions.BasePermission):
    """Allows access only to users in the 'Students' group."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _is_in_group(request.user, 'Students')

# Optional: More granular permission, e.g., IsTeacherOfCourse
# class IsTeacherOfCourse(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Assumes 'obj' is a Course instance or has a 'course' attribute
#         if hasattr(obj, 'teacher'): # If obj is Course
#              course_teacher = obj.teacher
#         elif hasattr(obj, 'course'): # If obj is Assignment, etc.
#              course_teacher = obj.course.teacher
#         else:
#              return False
#         return request.user == course_teacher and _is_in_group(request.user, 'Teachers')