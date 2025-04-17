# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints for the logged-in student
    path('my-courses/', views.MyCoursesListView.as_view(), name='my-courses'),
    path('my-assignments/', views.MyAssignmentsListView.as_view(), name='my-assignments'),
    path('my-grades/', views.MyGradesListView.as_view(), name='my-grades'),

    # Chatbot Endpoint
    path('chatbot/query/', views.ChatbotQueryView.as_view(), name='chatbot-query'),

    path('user/me/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Teacher specific URLs
    path('teacher/my-courses/', views.TeacherCoursesListView.as_view(), name='teacher-courses'),
    path('teacher/upload-content/', views.CourseContentUploadView.as_view(), name='upload-content'),
    # Example admin/general endpoints (if you add them)
    # path('courses/', views.CourseListCreateView.as_view(), name='course-list-create'),
]