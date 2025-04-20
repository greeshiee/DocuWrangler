from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import uuid
from openai import AzureOpenAI
import chromadb
from chromadb.config import Settings
from modules import config
from modules.extract import process_pdf_for_rag
from modules.qna import answer_question

app = Flask(__name__)
CORS(app)

# Initialize clients
def initialize_clients():
    # Initialize Azure OpenAI client
    azure_client = AzureOpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_version=config.AZURE_OPENAI_API_VERSION
    )
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path=config.CHROMA_DB_PATH
    )
    
    return azure_client, chroma_client

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    
    pdf_file = request.files['file']
    
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({"status": "error", "message": "File must be a PDF"}), 400
    
    # Generate a unique ID for the PDF
    pdf_id = request.form.get('pdf_id', str(uuid.uuid4()))
    
    try:
        # Read the PDF file
        pdf_bytes = pdf_file.read()
        
        # Initialize clients
        azure_client, chroma_client = initialize_clients()
        
        # Process the PDF for RAG
        result = process_pdf_for_rag(
            pdf_bytes=pdf_bytes,
            pdf_id=pdf_id,
            client=azure_client,
            chroma_client=chroma_client,
            config=config
        )
        
        # Return success response
        return jsonify({
            "status": "success", 
            "message": "PDF processed and indexed successfully",
            "pdf_id": pdf_id,
            "details": result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error processing PDF: {str(e)}"
        }), 500
    
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is working"})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"status": "error", "message": "No question provided"}), 400
    
    question = data['question']
    pdf_id = data.get('pdf_id')  # Optional: to limit search to a specific PDF
    
    # Call the answer_question function from qna.py
    result = answer_question(question, pdf_id)
    
    return jsonify(result)

# Ensure the ChromaDB directory exists
if not os.path.exists(config.CHROMA_DB_PATH):
    os.makedirs(config.CHROMA_DB_PATH)

if __name__ == '__main__':
    app.run(debug=True)
