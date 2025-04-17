# generate_ingestion_flowchart.py
import graphviz

dot = graphviz.Digraph('Content Ingestion', comment='Teacher Content Upload Flow', format='png')
dot.attr(rankdir='TB', label='Content Ingestion Flow', fontsize='16')

# Nodes
dot.node('TU', 'Teacher Uploads File\n(Streamlit UI)', shape='ellipse', style='filled', fillcolor='lightgreen')
dot.node('API', 'Backend API\n(/api/teacher/upload-content/)', shape='box')
dot.node('VAL', 'Validate Request\n(Is Teacher? Owns Course? File Type?)', shape='diamond', style='filled', fillcolor='lightgrey')
dot.node('SAVE', 'Save Original File\n(Media Folder: /course_name/)', shape='box')
# Optional: Create DB Record First
# dot.node('DBR', 'Create CourseMaterial Record (DB)', shape='box')
dot.node('PROC', 'Call process_and_embed_document', shape='box')
dot.node('EXT', 'Extract Text\n(PyPDF2/python-docx/read)', shape='box')
dot.node('CHK', 'Chunk Text\n(RecursiveCharacterTextSplitter)', shape='box')
dot.node('EMB', 'Embed Chunks\n(Google Embeddings)', shape='box')
dot.node('VDB', 'Add Chunks & Metadata to ChromaDB\n(incl. course_id)', shape='cylinder')
dot.node('SUCC', 'Return Success (201)', shape='ellipse', style='filled', fillcolor='lightgreen')
dot.node('FAIL', 'Return Error (500/400/403)', shape='ellipse', style='filled', fillcolor='lightcoral')
# Optional: Update DB Record Status
# dot.node('UPD', 'Update CourseMaterial Record (Processed=True/False)', shape='box')

# Edges
dot.edge('TU', 'API')
dot.edge('API', 'VAL')
dot.edge('VAL', 'SAVE' )
dot.edge('VAL', 'FAIL')
dot.edge('SAVE', 'PROC') # Assuming you create DB record within the view or after saving
# If creating DB Record first:
# dot.edge('VAL', 'DBR', label=' Valid')
# dot.edge('DBR', 'SAVE')
# dot.edge('SAVE', 'PROC')

dot.edge('PROC', 'EXT')
dot.edge('EXT', 'CHK')
dot.edge('CHK', 'EMB')
dot.edge('EMB', 'VDB')
dot.edge('VDB', 'SUCC') # Link success back to the API view's response
# If updating DB record:
# dot.edge('VDB', 'UPD', label=' Embedding OK')
# dot.edge('UPD', 'SUCC')


# Error path from processing
dot.edge('EXT', 'FAIL')
dot.edge('CHK', 'FAIL')
dot.edge('EMB', 'FAIL')
dot.edge('VDB', 'FAIL')

dot.render('content_ingestion_flowchart', view=False)
print("Generated content_ingestion_flowchart.png")