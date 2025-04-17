# generate_rag_flowchart.py
import graphviz

dot = graphviz.Digraph('RAG Pipeline', comment='Chatbot RAG Query Flow', format='png')
dot.attr(rankdir='TB', label='Chatbot RAG Query Flow', fontsize='16') # Top-to-Bottom layout

# Define nodes
dot.node('SQ', 'Student Asks Query\n(via Streamlit)', shape='ellipse', style='filled', fillcolor='lightblue')
dot.node('AQ', 'Backend API\n(/api/chatbot/query/)', shape='box')
dot.node('ID', 'Intent Check:\nAcademic or Content?', shape='diamond', style='filled', fillcolor='lightgrey')
dot.node('ACAD', 'Fetch Academic Data\n(DB Query)', shape='box')
# RAG Path
dot.node('ENR', 'Get Student\'s\nEnrolled Course IDs', shape='box')
dot.node('EQ', 'Embed User Query\n(Google Embeddings)', shape='box')
dot.node('VDB', 'Search ChromaDB\n(Filter by Course IDs)', shape='cylinder') # Cylinder for DB
dot.node('RC', 'Retrieve Relevant\nContext Chunks', shape='note')
dot.node('BP', 'Build Prompt\n(Query + Context + Template)', shape='box')
dot.node('LLM', 'Call Google LLM\n(Gemini Flash/Pro)', shape='cds') # CDS for external service
dot.node('FR', 'Format Response', shape='box')
dot.node('SR', 'Send Response\nto Streamlit', shape='ellipse', style='filled', fillcolor='lightblue')
dot.node('NF', '"Cannot Find Info"\nResponse', shape='box', style='filled', fillcolor='lightcoral')

# Define edges (connections)
dot.edge('SQ', 'AQ')
dot.edge('AQ', 'ID')

# Path for Academic Data
dot.edge('ID', 'ACAD', label=' Academic')
dot.edge('ACAD', 'FR')

# Path for RAG / Content Query
dot.edge('ID', 'ENR', label=' Content')
dot.edge('ENR', 'EQ')
dot.edge('EQ', 'VDB')
dot.edge('VDB', 'RC')
dot.edge('RC', 'BP')
# Add Query and Context to Prompt
dot.edge('EQ', 'BP', style='dashed', arrowhead='none')
dot.edge('RC', 'BP', style='dashed', arrowhead='none')
dot.edge('BP', 'LLM')
dot.edge('LLM', 'FR', label=' Answer Found')
dot.edge('LLM', 'NF', label=' Answer NOT Found') # LLM generates this based on prompt/context
dot.edge('NF', 'SR') # Send "Not Found" response
dot.edge('FR', 'SR')

# Render the graph
dot.render('rag_pipeline_flowchart', view=False) # view=False prevents opening the image automatically

print("Generated rag_pipeline_flowchart.png")