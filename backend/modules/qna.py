import os
from typing import List, Dict, Any, Optional, Tuple
from openai import AzureOpenAI
import chromadb
from chromadb.config import Settings
from modules import config

def initialize_clients():
    """Initialize and return Azure OpenAI and ChromaDB clients."""
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

def get_last_pdf_id(chroma_client) -> Optional[str]:
    """
    Retrieve the last PDF document ID from the vector database.
    Returns None if no documents found.
    """
    try:
        # Get the collection
        collection = chroma_client.get_collection("pdf_embeddings")
        
        # Query to get all documents
        results = collection.query(
            query_embeddings=[[0.0] * 3072],  # Dummy embedding
            n_results=1,
            include=["metadatas"]
        )
        
        if results and results["metadatas"] and results["metadatas"][0]:
            # Extract PDF ID from metadata
            return results["metadatas"][0][0].get("pdf_id")
        return None
    except Exception as e:
        print(f"Error retrieving last PDF ID: {str(e)}")
        
        # Alternative approach: try to list all collections
        try:
            collections = chroma_client.list_collections()
            if not collections:
                return None
            
            # Return the name of the first collection (assuming it's a PDF ID)
            return collections[0].name
        except:
            return None

def query_vector_db(question: str, pdf_id: str, azure_client: AzureOpenAI, 
                   chroma_client, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Query the vector database for relevant chunks with paragraph-level references.
    """
    try:
        # Get the collection
        collection = chroma_client.get_collection("pdf_embeddings")
        
        # Generate embedding for the question
        embedding_response = azure_client.embeddings.create(
            input=question,
            model=config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT
        )
        question_embedding = embedding_response.data[0].embedding
        
        # Query the collection with pdf_id filter
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
            where={"pdf_id": pdf_id} if pdf_id else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Process results
        relevant_chunks = []
        for i in range(len(results["ids"][0])):
            # Include paragraph reference for UI highlighting
            metadata = results["metadatas"][0][i]
            relevant_chunks.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": metadata,
                "similarity": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                "highlight_info": {
                    "page": metadata.get("page_num"),
                    "paragraph_index": metadata.get("paragraph_index"),
                    "position": {
                        "x0": metadata.get("position_x0"),
                        "y0": metadata.get("position_y0"),
                        "x1": metadata.get("position_x1"),
                        "y1": metadata.get("position_y1")
                    }
                }
            })
        
        # Sort by similarity (highest first)
        relevant_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        
        return relevant_chunks
    
    except Exception as e:
        print(f"Error querying vector database: {str(e)}")
        return []

def extract_confidence_and_references(answer_text: str) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Extract confidence score and references from the model's answer.
    Returns a tuple of (confidence_score, references).
    """
    confidence = 0.0
    references = []
    
    # Look for confidence score pattern (e.g., "Confidence: 0.8" or "Confidence score: 0.8")
    confidence_patterns = [
        "Confidence: ", 
        "Confidence score: ",
        "My confidence is ",
        "Confidence level: "
    ]
    
    for pattern in confidence_patterns:
        if pattern in answer_text:
            try:
                # Find the pattern and extract the number after it
                start_idx = answer_text.find(pattern) + len(pattern)
                end_idx = answer_text.find("\n", start_idx)
                if end_idx == -1:
                    end_idx = len(answer_text)
                
                confidence_str = answer_text[start_idx:end_idx].strip()
                # Extract the first number found
                import re
                confidence_match = re.search(r"(\d+\.\d+|\d+)", confidence_str)
                if confidence_match:
                    confidence = float(confidence_match.group(1))
                    if confidence > 1.0:  # Handle percentage format
                        confidence = confidence / 100.0
                break
            except:
                pass
    
    # Look for references pattern (e.g., "References: Page 1, Page 2" or "Sources: Page 1, Section A")
    reference_patterns = [
        "References:", 
        "Sources:",
        "Reference:",
        "Source:"
    ]
    
    for pattern in reference_patterns:
        if pattern in answer_text:
            try:
                # Find the pattern and extract the text after it
                start_idx = answer_text.find(pattern) + len(pattern)
                references_text = answer_text[start_idx:].strip()
                
                # Parse references - this is a simplified approach
                # In a real implementation, you might want more sophisticated parsing
                import re
                page_matches = re.findall(r"page (\d+)", references_text.lower())
                section_matches = re.findall(r"section ([a-z0-9\.]+)", references_text.lower())
                
                for page in page_matches:
                    references.append({"page": page})
                
                for section in section_matches:
                    references.append({"section": section})
                
                break
            except:
                pass
    
    return confidence, references

def generate_answer(question: str, relevant_chunks: List[Dict[str, Any]], 
                   azure_client: AzureOpenAI) -> Tuple[str, float, List[Dict[str, Any]]]:
    """
    Generate an answer with page references in text but paragraph-level info for UI.
    """
    if not relevant_chunks:
        return "I couldn't find any relevant information to answer your question.", 0.0, []
    
    # Prepare context from relevant chunks
    context_parts = []
    for chunk in relevant_chunks:
        metadata = chunk["metadata"]
        page_num = metadata.get("page_num", "unknown")
        
        # Add source information (only page number for the prompt)
        source_info = f"--- Content from page {page_num}"
        if "half" in metadata:
            source_info += f", {metadata['half']} half"
        source_info += " ---"
        
        # Add the content with its source
        context_parts.append(f"{source_info}\n{chunk['content']}")
    
    context = "\n\n".join(context_parts)
    
    # Prepare the prompt - only mention page numbers
    prompt = f"""
    Based on the following information from a PDF document, please answer the query.
    
    Query: {question}
    
    Document context:
    {context}
    
    Please provide a comprehensive answer based only on the information provided above.
    End your answer with:
    1. A confidence score between 0 and 1 indicating how confident you are in your answer.
    2. References to the specific pages from which you derived the answer.
    
    Format your response like this:
    
    [Your detailed answer here]
    
    Confidence: [score between 0 and 1]
    
    References: [list of page numbers used]
    """
    
    # Generate response
    response = azure_client.chat.completions.create(
        model=config.AZURE_OPENAI_VISION_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )
    
    answer_text = response.choices[0].message.content
    
    # Extract confidence and references from the answer
    confidence, page_references = extract_confidence_and_references(answer_text)
    
    # Create detailed references with paragraph info for UI highlighting
    detailed_references = []
    for chunk in relevant_chunks[:3]:  # Use top 3 chunks
        highlight_info = chunk.get("highlight_info", {})
        page_num = highlight_info.get("page", "unknown")
        
        detailed_references.append({
            "page": page_num,
            "paragraph_index": highlight_info.get("paragraph_index"),
            "position": highlight_info.get("position", {}),
            "preview": chunk["metadata"].get("preview", ""),
            "similarity": chunk["similarity"]
        })
    
    # If no confidence was extracted, calculate based on chunk similarities
    if confidence == 0.0 and relevant_chunks:
        confidence = sum(chunk["similarity"] for chunk in relevant_chunks[:3]) / min(3, len(relevant_chunks))
    
    return answer_text, confidence, detailed_references

def answer_question(question: str, pdf_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to answer a question with paragraph-level references for UI highlighting.
    """
    # Initialize clients
    azure_client, chroma_client = initialize_clients()
    
    # If pdf_id is not provided, get the last PDF ID
    if not pdf_id:
        pdf_id = get_last_pdf_id(chroma_client)
        if not pdf_id:
            return {
                "status": "error",
                "message": "No PDF documents found in the database."
            }
    
    # Query the vector database
    relevant_chunks = query_vector_db(
        question=question,
        pdf_id=pdf_id,
        azure_client=azure_client,
        chroma_client=chroma_client,
        top_k=5
    )
    
    # Generate answer
    answer_text, confidence, detailed_references = generate_answer(
        question=question,
        relevant_chunks=relevant_chunks,
        azure_client=azure_client
    )
    
    # Format simple page references for display in the answer
    page_references = [f"Page {ref['page']}" for ref in detailed_references]
    
    # Return the result with both simple page references and detailed highlighting info
    return {
        "status": "success",
        "answer": answer_text,
        "confidence": round(confidence, 2),
        "references": page_references,  # Simple page references for display
        "highlight_info": detailed_references,  # Detailed info for UI highlighting
        "pdf_id": pdf_id
    }

# For direct testing of this module
if __name__ == "__main__":
    test_question = "What is the main topic of this document?"
    result = answer_question(test_question)
    print(f"Question: {test_question}")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    print(f"References: {', '.join(result['references'])}")
