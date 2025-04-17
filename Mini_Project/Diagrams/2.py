# generate_backend_diagram.py
from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import Django, Fastapi # Using FastAPI icon for DRF
from diagrams.programming.language import Python
from diagrams.onprem.database import Postgresql
from diagrams.generic.database import SQL # Chroma
# --- USE AIPlatform ---
from diagrams.gcp.ml import AIPlatform # Use AI Platform icon
# --- END CHANGE ---


graph_attr = {
    "fontsize": "12",
    "bgcolor": "white"
}

# Ensure you are setting the filename correctly
output_filename = "backend_architecture"

with Diagram("Backend API Architecture (Django)", show=False, filename=output_filename, graph_attr=graph_attr):

    api_client = Fastapi("API Client (Streamlit)") # Representing the frontend calling the API

    with Cluster("Django Backend ('api' app & 'core_settings')"):
        drf_urls = Django("urls.py (API Routes)")

        with Cluster("API Logic"):
            views = Python("Views (DRF Views, APIView)")
            serializers = Python("Serializers")
            permissions = Python("Permissions (IsStudent/IsTeacher)")
            chatbot_utils = Python("chatbot_utils.py")

        with Cluster("Data Layer"):
            models = Python("Models.py")
            orm = Django("Django ORM")

    # External Services
    postgres_db = Postgresql("PostgreSQL")
    vector_db = SQL("ChromaDB")
    # --- USE AIPlatform ---
    google_ai = AIPlatform("Google AI") # Use the imported node
    # --- END CHANGE ---

    # Connections
    api_client >> drf_urls >> views

    views >> serializers
    views >> permissions
    views >> models
    views >> chatbot_utils # Views call utils

    # Logic connecting to ORM
    views >> orm
    chatbot_utils >> orm # Utils might interact with DB via models

    # ORM to DB
    orm >> postgres_db

    # Chatbot Utils connecting to AI/Vector DB
    chatbot_utils >> Edge(label="Embed/Store/Retrieve") >> vector_db
    chatbot_utils >> Edge(label="Call API") >> google_ai # Utils call embedding API via Langchain
    views >> Edge(label="Call LLM") >> google_ai # Views call LLM via Langchain

    # Serializers interact with Models
    serializers >> models

print(f"Generated {output_filename}.png")