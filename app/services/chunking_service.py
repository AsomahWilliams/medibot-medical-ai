
"""
Chunking Pipeline Service
Handles document chunking configuration and processing
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from typing import List, Dict, Any


# Chunking Configuration
CHUNK_CONFIG = {
    "chunk_size": 300,
    "chunk_overlap": 50,
    "separators": ["\n\n", "\n", " ", ""],
    "length_function": len
}


def get_text_splitter():
    """Get the configured text splitter"""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_CONFIG["chunk_size"],
        chunk_overlap=CHUNK_CONFIG["chunk_overlap"],
        separators=CHUNK_CONFIG["separators"],
        length_function=CHUNK_CONFIG["length_function"]
    )


def process_document(file_path: str, doc_type: str = "general", user_id: str = None) -> List:
    """
    Process a document and return chunks with metadata
    
    Args:
        file_path: Path to the document
        doc_type: Type of document (ghana_health, user_upload)
        user_id: User ID for user uploads
    
    Returns:
        List of document chunks with metadata
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    
    # Add metadata to each chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["total_chunks"] = len(chunks)
        chunk.metadata["doc_type"] = doc_type
        chunk.metadata["source"] = chunk.metadata.get("source", file_path)
        
        if user_id:
            chunk.metadata["user_id"] = user_id
    
    return chunks


def get_chunking_info() -> Dict[str, Any]:
    """Get chunking configuration info"""
    return {
        "chunk_size": CHUNK_CONFIG["chunk_size"],
        "chunk_overlap": CHUNK_CONFIG["chunk_overlap"],
        "separators": CHUNK_CONFIG["separators"],
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384
    }
