import base64
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Any, Optional
import chromadb
from openai import AzureOpenAI
import os

def create_collection_if_not_exists(chroma_client, collection_name: str):
    """Create a collection if it doesn't exist already."""
    try:
        return chroma_client.get_collection(collection_name)
    except:
        return chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Using cosine similarity
        )
import fitz
import base64
from typing import List, Dict, Any, Optional

def extract_text_and_images_from_pdf(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extract text and images from PDF, handling brochure format with two columns per half-page.
    
    Returns a list of content blocks, each containing:
    - type: "text" or "image"
    - content: text string or base64 encoded image
    - page_num: page number
    - position: position information
    """
    content_blocks = []
    
    # Open the PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num, page in enumerate(doc):
        # Extract images first
        image_blocks = extract_images_from_page(doc, page, page_num)
        content_blocks.extend(image_blocks)
        
        # Extract text
        text_blocks = extract_text_from_page(page, page_num)
        content_blocks.extend(text_blocks)
    
    return content_blocks

def extract_images_from_page(doc, page, page_num: int) -> List[Dict[str, Any]]:
    """
    Extract images from a PDF page safely.
    
    Args:
        doc: The fitz document
        page: The page object
        page_num: The page number (0-based)
        
    Returns:
        List of image content blocks
    """
    image_blocks = []
    
    try:
        # Method 1: Try using get_images() for standard images
        image_list = page.get_images(full=True)
        for img in image_list:
            try:
                xref = img[0]  # Extract the xref
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to base64 for storage and API response
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                
                # Find image position using a safer approach
                position = find_image_position(page, xref)
                
                image_blocks.append({
                    "type": "image",
                    "content": base64_image,
                    "page_num": page_num + 1,
                    "position": position,
                    "mime_type": base_image["ext"]
                })
            except Exception as e:
                print(f"Error extracting image with xref {xref}: {str(e)}")
                continue
    except Exception as e:
        print(f"Error getting images from page {page_num + 1}: {str(e)}")
    
    # Method 2: Try using get_text("dict") for inline images
    try:
        blocks = page.get_text("dict")["blocks"]
        for block_idx, block in enumerate(blocks):
            if block.get('type') == 1:  # Image block
                try:
                    # For inline images
                    img_bytes = block.get('image', b'')
                    if img_bytes:
                        base64_image = base64.b64encode(img_bytes).decode("utf-8")
                        
                        # Get position from block
                        bbox = block.get('bbox', (0, 0, 100, 100))
                        position = {"x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3]}
                        
                        image_blocks.append({
                            "type": "image",
                            "content": base64_image,
                            "page_num": page_num + 1,
                            "position": position,
                            "mime_type": "png"  # Default to PNG for inline images
                        })
                except Exception as e:
                    print(f"Error extracting inline image: {str(e)}")
                    continue
    except Exception as e:
        print(f"Error getting text blocks from page {page_num + 1}: {str(e)}")
    
    return image_blocks

def find_image_position(page, xref: int) -> Dict[str, float]:
    """
    Find the position of an image on a page safely.
    
    Args:
        page: The page object
        xref: The image reference
        
    Returns:
        A dictionary with position information
    """
    # Default position if we can't find it
    position = {"x0": 0, "y0": 0, "x1": 100, "y1": 100}
    
    try:
        # Try using get_image_bbox with a rect
        for img in page.get_images():
            if img[0] == xref:
                # Create a rectangle for the image
                rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                img_rect = page.get_image_bbox(img, rect)
                if img_rect:
                    position = {"x0": img_rect.x0, "y0": img_rect.y0, 
                                "x1": img_rect.x1, "y1": img_rect.y1}
                break
    except Exception:
        # If that fails, try using get_text("dict") to find images
        try:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get('type') == 1:  # Image block
                    # This is an image block
                    bbox = block.get('bbox', (0, 0, 100, 100))
                    position = {"x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3]}
                    break
        except Exception:
            # Keep the default position
            pass
    
    return position

def extract_text_from_page(page, page_num: int) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF page, handling brochure format.
    
    Args:
        page: The page object
        page_num: The page number (0-based)
        
    Returns:
        List of text content blocks
    """
    text_blocks = []
    page_width, page_height = page.rect.width, page.rect.height
    
    # Check if this is a full-page (content spans entire page)
    # This is a simple heuristic - you may need to adjust based on your specific PDFs
    try:
        text_blocks_raw = page.get_text("blocks")
        x_positions = [block[0] for block in text_blocks_raw]
        is_full_page = len(set([int(x/100) for x in x_positions])) > 2
    except Exception:
        # If we can't determine, assume it's a full page
        is_full_page = True
    
    try:
        if is_full_page:
            # Process as a single full page
            text = page.get_text("text")
            if text.strip():
                text_blocks.append({
                    "type": "text",
                    "content": text,
                    "page_num": page_num + 1,
                    "position": {"x0": 0, "y0": 0, "x1": page_width, "y1": page_height},
                    "is_full_page": True
                })
        else:
            # Process as a two-column half-page
            half_width = page_width / 2
            
            # Extract left half
            left_text = extract_text_from_rect(page, (0, 0, half_width, page_height))
            if left_text.strip():
                text_blocks.append({
                    "type": "text",
                    "content": left_text,
                    "page_num": page_num + 1,
                    "position": {"x0": 0, "y0": 0, "x1": half_width, "y1": page_height},
                    "is_full_page": False,
                    "half": "left"
                })
            
            # Extract right half
            right_text = extract_text_from_rect(page, (half_width, 0, page_width, page_height))
            if right_text.strip():
                text_blocks.append({
                    "type": "text",
                    "content": right_text,
                    "page_num": page_num + 1,
                    "position": {"x0": half_width, "y0": 0, "x1": page_width, "y1": page_height},
                    "is_full_page": False,
                    "half": "right"
                })
    except Exception as e:
        print(f"Error extracting text from page {page_num + 1}: {str(e)}")
        # Fallback: try to get any text we can
        try:
            text = page.get_text("text")
            if text.strip():
                text_blocks.append({
                    "type": "text",
                    "content": text,
                    "page_num": page_num + 1,
                    "position": {"x0": 0, "y0": 0, "x1": page_width, "y1": page_height},
                    "is_full_page": True
                })
        except Exception:
            pass
    
    return text_blocks

def extract_text_from_rect(page, rect):
    """Extract text from a specific rectangle on the page."""
    try:
        # Get all words on the page
        words = page.get_text("words")
        
        # Filter words that fall within the rectangle
        x0, y0, x1, y1 = rect
        filtered_words = [
            word for word in words
            if word[0] >= x0 and word[2] <= x1 and word[1] >= y0 and word[3] <= y1
        ]
        
        # Sort words by their y-position (top to bottom) and then x-position (left to right)
        filtered_words.sort(key=lambda w: (w[3], w[0]))
        
        # Group words by lines
        lines = []
        current_line = []
        current_y = None
        
        for word in filtered_words:
            word_x0, word_y0, word_x1, word_y1, text, block_no, line_no, word_no = word
            
            # If this is a new line or the first word
            if current_y is None or abs(word_y0 - current_y) > 5:  # Threshold for new line
                if current_line:
                    lines.append(current_line)
                current_line = [word]
                current_y = word_y0
            else:
                current_line.append(word)
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        # Reconstruct text by lines
        text_content = []
        for line in lines:
            line_text = " ".join([word[4] for word in line])
            text_content.append(line_text)
        
        return "\n".join(text_content)
    except Exception as e:
        print(f"Error extracting text from rectangle: {str(e)}")
        return ""


def create_intelligent_chunks(content_blocks: List[Dict[str, Any]], max_chunk_size=1000, overlap=200):
    """
    Create intelligent chunks from the extracted content blocks.
    This helps in creating more meaningful semantic units for embedding.
    """
    chunks = []
    
    # Group content blocks by page
    pages = {}
    for block in content_blocks:
        page_num = block["page_num"]
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(block)
    
    # Process each page
    for page_num, page_blocks in sorted(pages.items()):
        # Process text blocks
        text_blocks = [block for block in page_blocks if block["type"] == "text"]
        
        for text_block in text_blocks:
            text = text_block["content"]
            
            # If text is smaller than max chunk size, keep it as is
            if len(text) <= max_chunk_size:
                chunks.append({
                    **text_block,
                    "chunk_type": "text_chunk"
                })
            else:
                # Split larger text with overlap
                for i in range(0, len(text), max_chunk_size - overlap):
                    chunk_text = text[i:i + max_chunk_size]
                    if len(chunk_text) > 50:  # Minimum meaningful chunk size
                        chunks.append({
                            **text_block,
                            "content": chunk_text,
                            "chunk_type": "text_chunk",
                            "is_partial": True,
                            "chunk_start": i,
                            "chunk_end": min(i + max_chunk_size, len(text))
                        })
        
        # Process image blocks - each image is its own chunk
        image_blocks = [block for block in page_blocks if block["type"] == "image"]
        for image_block in image_blocks:
            chunks.append({
                **image_block,
                "chunk_type": "image_chunk"
            })
    
    return chunks

def generate_multimodal_embeddings(content_blocks: List[Dict[str, Any]], client: AzureOpenAI, config):
    """
    Generate embeddings for both text and images using Azure OpenAI.
    
    Returns the original content blocks with embeddings added.
    """
    for block in content_blocks:
        if block["type"] == "text":
            # For text blocks, we'll use the text directly
            response = client.embeddings.create(
                input=block["content"],
                model=config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT  # Your text embedding model deployment
            )
            block["embedding"] = response.data[0].embedding
            
        elif block["type"] == "image":
            # For image blocks, we'll use GPT-4o's multimodal capabilities
            # Convert base64 back to image for processing
            image_data = base64.b64decode(block["content"])
            
            # Use GPT-4o to generate a description of the image
            messages = [
                {"role": "system", "content": "You are an AI assistant that describes images in detail."},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Please describe this image in detail."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{block['mime_type']};base64,{block['content']}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Get image description from GPT-4o
            chat_response = client.chat.completions.create(
                model=config.AZURE_OPENAI_VISION_DEPLOYMENT,  # Your GPT-4o deployment
                messages=messages,
                max_tokens=300
            )
            
            image_description = chat_response.choices[0].message.content
            block["description"] = image_description
            
            # Now get embedding for the image description
            response = client.embeddings.create(
                input=image_description,
                model=config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT
            )
            block["embedding"] = response.data[0].embedding
    
    return content_blocks

def store_embeddings(chroma_client, pdf_id: str, content_blocks: List[Dict[str, Any]]):
    """Store embeddings in ChromaDB with paragraph-level references."""
    collection = create_collection_if_not_exists(chroma_client, "pdf_embeddings")
    
    # Prepare data for batch insertion
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for i, block in enumerate(content_blocks):
        block_id = f"{pdf_id}_{i}"
        ids.append(block_id)
        embeddings.append(block["embedding"])
        
        # Store more granular metadata for UI highlighting
        metadata = {
            "pdf_id": pdf_id,
            "page_num": block["page_num"],
            "type": block["type"],
            "position_x0": block["position"]["x0"],
            "position_y0": block["position"]["y0"],
            "position_x1": block["position"]["x1"],
            "position_y1": block["position"]["y1"],
            "chunk_id": i,  # Unique identifier for this chunk
            "paragraph_index": i  # Can be used for highlighting
        }
        
        # Add text-specific metadata
        if block["type"] == "text":
            if "is_full_page" in block:
                metadata["is_full_page"] = block["is_full_page"]
            if "half" in block:
                metadata["half"] = block["half"]
            
            # Add first 50 chars as a preview for UI
            metadata["preview"] = block["content"][:50] + "..." if len(block["content"]) > 50 else block["content"]
            documents.append(block["content"])
        else:
            # For image blocks
            metadata["mime_type"] = block["mime_type"]
            documents.append(block["description"])
        
        metadatas.append(metadata)
    
    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    return {"message": f"Successfully stored {len(ids)} embeddings for PDF {pdf_id}"}

def handle_table_content(page):
    """
    Handle content that's often recognized as tables.
    This function extracts text in a structured way when table detection is problematic.
    """
    # Get words with positions
    words = page.get_text("words")
    
    # Sort words by their y-position (top to bottom)
    words.sort(key=lambda w: w[3])
    
    # Group words by lines (similar y-positions)
    lines = []
    current_line = []
    current_y = None
    
    for word in words:
        x0, y0, x1, y1, text, block_no, line_no, word_no = word
        
        # If this is a new line or the first word
        if current_y is None or abs(y0 - current_y) > 5:  # Threshold for new line
            if current_line:
                lines.append(current_line)
            current_line = [word]
            current_y = y0
        else:
            current_line.append(word)
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    # For each line, sort words by x-position (left to right)
    structured_content = []
    for line in lines:
        line.sort(key=lambda w: w[0])
        line_text = " ".join([word[4] for word in line])
        structured_content.append(line_text)
    
    return "\n".join(structured_content)

def detect_columns(page):
    """
    Detect columns within a page based on text block positions.
    Returns a list of column boundaries (x0, x1).
    """
    blocks = page.get_text("blocks")
    
    # Extract x-coordinates of all blocks
    x_coords = []
    for block in blocks:
        x0, y0, x1, y1, text, block_no, block_type = block
        x_coords.append(x0)
        x_coords.append(x1)
    
    # Use a histogram approach to find column boundaries
    hist, bin_edges = np.histogram(x_coords, bins=20)
    
    # Find peaks in the histogram
    peaks = []
    for i in range(1, len(hist)-1):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 2:
            peaks.append(bin_edges[i])
    
    # Sort peaks to get column boundaries
    peaks.sort()
    
    # Convert peaks to column boundaries
    columns = []
    if len(peaks) >= 2:
        # Multiple columns detected
        for i in range(len(peaks)-1):
            columns.append((peaks[i], peaks[i+1]))
    else:
        # Single column (full page width)
        columns.append((0, page.rect.width))
    
    return columns

def split_pdf_bytes_to_pages(pdf_bytes: bytes) -> List[bytes]:
    """
    Split PDF bytes into a list of PDF bytes, each representing a single page.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_bytes_list = []
    
    for page_num in range(len(doc)):
        # Create a new PDF in memory for each page
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        page_bytes = new_doc.write()
        page_bytes_list.append(page_bytes)
        new_doc.close()
    
    doc.close()
    return page_bytes_list
    
def process_pdf_for_rag(pdf_bytes: bytes, pdf_id: str, client: AzureOpenAI, chroma_client, config):
    """
    Complete pipeline to process a PDF for RAG:
    1. Split PDF into individual pages for efficient processing
    2. Process each page separately:
       a. Extract text and images
       b. Create intelligent chunks
       c. Generate embeddings
    3. Store all embeddings under a single pdf_id for unified retrieval
    """
    # Split PDF into individual pages
    page_bytes_list = split_pdf_bytes_to_pages(pdf_bytes)
    
    all_content_blocks = []
    all_chunked_blocks = []
    all_blocks_with_embeddings = []
    
    # Process each page separately for efficiency
    for page_idx, page_bytes in enumerate(page_bytes_list):
        # Extract content from this page
        content_blocks = extract_text_and_images_from_pdf(page_bytes)
        
        # Update the page number to reflect the actual page in the document
        for block in content_blocks:
            block["page_num"] = page_idx + 1
        
        all_content_blocks.extend(content_blocks)
        
        # Create intelligent chunks for this page
        chunked_blocks = create_intelligent_chunks(content_blocks)
        all_chunked_blocks.extend(chunked_blocks)
        
        # Generate embeddings for this page
        blocks_with_embeddings = generate_multimodal_embeddings(chunked_blocks, client, config)
        all_blocks_with_embeddings.extend(blocks_with_embeddings)
        
        print(f"Processed page {page_idx+1}/{len(page_bytes_list)}")
    
    # Store all embeddings under a single pdf_id
    storage_result = store_embeddings(chroma_client, pdf_id, all_blocks_with_embeddings)
    
    # Return summary of the entire process
    return {
        "pdf_id": pdf_id,
        "num_pages": len(page_bytes_list),
        "num_text_blocks": sum(1 for block in all_content_blocks if block["type"] == "text"),
        "num_image_blocks": sum(1 for block in all_content_blocks if block["type"] == "image"),
        "num_chunks": len(all_chunked_blocks),
        "pages_processed": len(page_bytes_list),
        "storage_result": storage_result
    }


