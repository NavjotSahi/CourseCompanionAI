# backend/api/views.py

import os
from dotenv import load_dotenv
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Enrollment, Assignment, Grade
from .serializers import (
    UserSerializer,
    CourseSerializer,
    AssignmentSerializer,
    GradeSerializer,
    StudentEnrollmentSerializer
)
from .permissions import IsTeacher, IsStudent
from .chatbot_utils import process_and_embed_document

# Load environment variables
load_dotenv()

# --- Google GenAI Setup ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

llm, embeddings_model, vectorstore = None, None, None
google_api_key = os.getenv('GOOGLE_API_KEY')

if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
        embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        project_root = os.path.dirname(settings.BASE_DIR)
        persist_directory = os.path.join(project_root, 'chroma_db_persistent')
        os.makedirs(persist_directory, exist_ok=True)

        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings_model,
            collection_name="course_content"
        )
    except Exception as e:
        print(f"ERROR: GenAI init failed: {e}")
else:
    print("ERROR: GOOGLE_API_KEY not found. Chatbot disabled.")

# --- User Info ---
class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        groups = list(user.groups.values_list('name', flat=True))
        serializer = UserSerializer(user)
        data = serializer.data
        data['groups'] = groups
        return Response(data)

# --- Student Views ---
class MyCoursesListView(generics.ListAPIView):
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course', 'course__teacher')

class MyAssignmentsListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        user = self.request.user
        enrolled_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
        queryset = Assignment.objects.filter(course_id__in=enrolled_ids).select_related('course')
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset.order_by('due_date')

class MyGradesListView(generics.ListAPIView):
    serializer_class = GradeSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        user = self.request.user
        queryset = Grade.objects.filter(student=user).select_related('assignment', 'assignment__course')
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(assignment__course_id=course_id)
        return queryset.order_by('assignment__due_date')

# --- Teacher Views ---
class TeacherCoursesListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

class CourseContentUploadView(APIView):
    permission_classes = [IsTeacher]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        course_id = request.data.get('course_id')

        if not file_obj or not course_id:
            return Response({"error": "Missing file or course_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = get_object_or_404(Course, pk=course_id)
            if course.teacher != request.user:
                return Response({"error": "Not authorized for this course."}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"error": "Invalid Course ID."}, status=status.HTTP_400_BAD_REQUEST)

        allowed_extensions = ['.pdf', '.docx', '.txt']
        filename, extension = os.path.splitext(file_obj.name)
        if extension.lower() not in allowed_extensions:
            return Response({"error": f"Unsupported file type: {extension}"}, status=status.HTTP_400_BAD_REQUEST)

        file_name = default_storage.save(f"course_{course_id}/{file_obj.name}", file_obj)
        file_path = default_storage.path(file_name)

        if not vectorstore or not embeddings_model:
            return Response({"error": "Chatbot components not ready. Cannot process file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        success = process_and_embed_document(
            file_path=file_path,
            course_id=course.id,
            original_filename=file_obj.name,
            vectorstore=vectorstore,
            embeddings_model=embeddings_model
        )

        if success:
            return Response({"message": f"File '{file_obj.name}' added for course {course.code}."}, status=status.HTTP_201_CREATED)
        else:
            if default_storage.exists(file_name):
                default_storage.delete(file_name)
            return Response({"error": "Failed to embed document."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Chatbot Logic ---
def get_academic_data(user, query):
    query_lower = query.lower()
    if "grade" in query_lower:
        grades = Grade.objects.filter(student=user).select_related('assignment', 'assignment__course')
        if grades.exists():
            return "Here are your recent grades:\n" + "\n".join(
                f"- {g.assignment.course.code}: {g.assignment.title} - {g.score}/{g.assignment.total_points if g.score else 'Not Graded'}"
                for g in grades[:5]
            )
        return "No grades found."

    elif "assignment" in query_lower or "due" in query_lower:
        assignments = Assignment.objects.filter(course__enrollments__student=user).select_related('course').order_by('due_date')
        if assignments.exists():
            return "Upcoming assignments:\n" + "\n".join(
                f"- {a.course.code}: {a.title} (Due: {a.due_date.strftime('%Y-%m-%d %H:%M')})"
                for a in assignments[:5]
            )
        return "No upcoming assignments."

    elif "course" in query_lower or "enrolled" in query_lower:
        enrollments = Enrollment.objects.filter(student=user).select_related('course')
        if enrollments.exists():
            return "You are enrolled in:\n" + "\n".join(
                f"- {e.course.code}: {e.course.name}" for e in enrollments
            )
        return "No courses found."

    return None

def get_course_content_answer(user, query):
    if not (llm and vectorstore and embeddings_model):
        return "Chatbot is currently unavailable. Please try again later."

    enrolled_ids = list(Enrollment.objects.filter(student=user).values_list("course_id", flat=True))
    if not enrolled_ids:
        return "You are not enrolled in any courses with available content."

    try:
        retriever = vectorstore.as_retriever(search_kwargs={
            "k": 4,
            "filter": {"course_id": {"$in": [str(cid) for cid in enrolled_ids]}}
        })

        prompt_template = """
        You are an assistant helping a student. Use ONLY the following context from course materials to answer.
        If not found, say: "I cannot find that information in the provided course materials for your enrolled courses."

        Context:
        {context}

        Question: {question}

        Answer:"""
        qa_prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": qa_prompt}
        )

        result = qa_chain.invoke({"query": query})
        answer = result.get('result', '').strip()

        return answer if answer else "I cannot find that information in the provided course materials."

    except Exception as e:
        print(f"Chatbot error: {e}")
        return "Something went wrong while processing your question."

class ChatbotQueryView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        user = request.user
        user_query = request.data.get('query', '').strip()

        if not user_query:
            return Response({"error": "Query cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        academic_response = get_academic_data(user, user_query)
        if academic_response:
            return Response({"response": academic_response})

        content_response = get_course_content_answer(user, user_query)
        return Response({"response": content_response})