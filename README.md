# AI-Powered Academic Dashboard & Course-Specific Chatbot 🎓🤖

A full-stack educational platform that combines a personalized student dashboard with a course-specific chatbot powered by Retrieval-Augmented Generation (RAG) and generative AI. Built to enhance learning through real-time academic tracking and intelligent, document-grounded interactions.

## 🔍 Overview

This project integrates:
- 📊 **Student Dashboard**: Visualizes grades, assignments, and course progress in real time.
- 💬 **RAG-based Chatbot**: Answers academic queries using course-specific materials uploaded by instructors.
- 🔐 **Role-Based Access**: Secure login system for students, instructors, and admins with JWT authentication.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) for interactive dashboards and chatbot UI
- **Backend**: [Django REST Framework](https://www.django-rest-framework.org/) for APIs and user management
- **AI Orchestration**: [LangChain](https://www.langchain.com/) + [Google Gemini](https://deepmind.google/technologies/gemini/)
- **Database**: PostgreSQL (for academic data), ChromaDB (for vector embeddings)
- **Auth**: JSON Web Tokens (JWT), Role-based access (students/teachers/admins)

## ✨ Features

- 📚 Instructor upload portal for course materials (PDF, DOCX, TXT)
- 🧠 Chatbot grounded in course content using vector search + RAG
- 🔒 Secure login with custom user roles
- 📈 Dashboard with student performance and deadline tracking
- 💬 Real-time academic Q&A with citation-backed responses

## 📦 Folder Structure

```bash
├── backend/                       # Backend logic powered by Django REST Framework
│   ├── api/                       # Core API components (chatbot logic, models, etc.)
│   │   ├── chatbot_utils.py       # Utilities for chatbot logic and RAG handling
│   │   ├── models.py              # Django ORM models (User, Course, Document, etc.)
│   │   ├── permissions.py         # Custom role-based access controls (e.g., Student, Instructor)
│   │   ├── serializers.py         # Data validation and serialization for API inputs/outputs
│   │   ├── url.py                 # Route definitions specific to the API
│   │   ├── views.py               # API view logic (RAG endpoints, file upload, etc.)
│   ├── core_settings/            # Global Django project settings and configuration
│   │   ├── urls.py                # Root URL routing for the backend server
│   ├── manage.py                 # Django CLI entry point
│
├── frontend_dashboard/           # Streamlit-based user-facing dashboard
│   ├── app.py                    # Main Streamlit app (login, chatbot, performance dashboard)
│   ├── requirements.txt          # Python dependencies for the frontend
│
├── Diagrams/                     # Architecture diagrams (LangChain pipeline, system design)
│
├── chroma_db_persistent/         # Local ChromaDB vector store (persisted embeddings + metadata)
│
├── media_files/                  # Uploaded course materials (PDFs, docs) by educators
│
├── README.md                     # Project overview, setup instructions, and usage guide
