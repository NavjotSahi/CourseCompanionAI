# generate_system_diagram.py
from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Python
from diagrams.onprem.database import Postgresql
from diagrams.onprem.inmemory import Redis # Example if using Celery later
from diagrams.onprem.queue import Celery # Example if using Celery later
from diagrams.generic.compute import Rack # Represents generic servers/services
from diagrams.generic.database import SQL # Represents Vector DB Chroma
# --- USE AIPlatform ---
from diagrams.gcp.ml import AIPlatform # Use AI Platform icon as representation
# --- END CHANGE ---
from diagrams.aws.network import ELB # Representing a generic Load Balancer/Proxy
from diagrams.aws.compute import EC2 # Representing Frontend/Backend servers

# Increased graph attributes for better spacing
graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "splines": "spline", # Use curved lines
    "nodesep": "1.0",    # Increase separation between nodes
    "ranksep": "1.5",    # Increase separation between ranks (layers)
}
output_filename = "system_architecture" 

with Diagram("System Architecture", show=False, filename=output_filename, graph_attr=graph_attr, direction="LR"):

    user = Rack("User (Student/Teacher)")

    with Cluster("Frontend (Streamlit)"):
        streamlit_app = EC2("Streamlit App")

    with Cluster("Backend Services (Django)"):
        
        django_app = EC2("Django API")
        with Cluster("Databases"):
            postgres_db = Postgresql("PostgreSQL (Academic Data)")
            vector_db = SQL("ChromaDB (Vector Store)")

    google_ai = AIPlatform("Google AI (Gemini/Embeddings)")

    user >> streamlit_app

    streamlit_app >> Edge(label="API Calls (Auth, Data, Chatbot, Upload)", style="dashed") >> django_app

    django_app >> Edge(label="Read/Write") >> postgres_db
    django_app >> Edge(label="Read/Write Embeddings") >> vector_db
    django_app >> Edge(label="LLM/Embedding API Calls", style="dashed") >> google_ai

print(f"Generated {output_filename}.png")