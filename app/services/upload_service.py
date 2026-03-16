# ============================================
# UPLOAD SERVICE
# ============================================
import os
import logging
import uuid
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings

# ============================================
# CONFIGURATION
# ============================================
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# PINECONE CONFIGURATION
# ============================================
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medicalindex")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# ============================================
# PDF UPLOAD
# ============================================
def upload_pdf(file_path: str, source: str = "unknown") -> Dict[str, Any]:
    """
    Upload PDF to Pinecone vector store
    
    Args:
        file_path: Path to the PDF file
        source: Source identifier for the document
        
    Returns:
        Dictionary with upload status and metadata
    """
    try:
        # Check if Pinecone is configured
        if not PINECONE_API_KEY:
            raise Exception("Pinecone API key not configured")
        
        if not PINECONE_INDEX_NAME:
            raise Exception("Pinecone index name not configured")
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Copy file to upload directory
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(UPLOAD_DIR, file_name)
        
        import shutil
        shutil.copy2(file_path, destination_path)
        
        # Load PDF
        logger.info(f"Loading PDF: {file_name}")
        loader = PyPDFLoader(destination_path)
        documents = loader.load()
        
        # Split documents
        logger.info(f"Splitting documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata["source"] = source
            chunk.metadata["filename"] = file_name
        
        # Create embeddings
        logger.info("Creating embeddings")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Connect to Pinecone
        logger.info(f"Connecting to Pinecone index: {PINECONE_INDEX_NAME}")
        vectorstore = Pinecone.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=PINECONE_INDEX_NAME
        )
        
        logger.info(f"Successfully uploaded {len(chunks)} chunks to Pinecone")
        
        return {
            "status": "success",
            "message": f"Uploaded {file_name} with {len(chunks)} chunks",
            "chunks": len(chunks),
            "source": source,
            "filename": file_name
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}",
            "chunks": 0,
            "source": source,
            "filename": file_name
        }

# ============================================
# DELETE FROM PINECONE
# ============================================
def delete_from_pinecone(source: str) -> Dict[str, Any]:
    """
    Delete documents from Pinecone by source
    
    Args:
        source: Source identifier to delete
        
    Returns:
        Dictionary with deletion status
    """
    try:
        if not PINECONE_API_KEY:
            raise Exception("Pinecone API key not configured")
        
        if not PINECONE_INDEX_NAME:
            raise Exception("Pinecone index name not configured")
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vectorstore = Pinecone.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        
        # Delete by filter
        vectorstore.delete(filter={"source": source})
        
        logger.info(f"Deleted documents with source: {source}")
        
        return {
            "status": "success",
            "message": f"Deleted documents with source: {source}"
        }
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return {
            "status": "error",
            "message": f"Delete failed: {str(e)}"
        }

# ============================================
# CHECK INDEX STATUS (FIXED)
# ============================================
def check_index_status() -> Dict[str, Any]:
    """
    Check Pinecone index status
    
    Returns:
        Dictionary with index status
    """
    try:
        if not PINECONE_API_KEY:
            return {"status": "unhealthy", "error": "API key not configured"}
        
        if not PINECONE_INDEX_NAME:
            return {"status": "unhealthy", "error": "Index name not configured"}
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vectorstore = Pinecone.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        
        # Get index stats (new API)
        try:
            index_stats = vectorstore._index.describe_index_stats()
            total_documents = index_stats.get("namespaces", {}).get("{}", {}).get("vector_count", 0)
            dimensions = index_stats.get("dimension", 0)
        except Exception:
            total_documents = "unknown"
            dimensions = "unknown"
        
        return {
            "status": "healthy",
            "index_name": PINECONE_INDEX_NAME,
            "total_documents": total_documents,
            "dimensions": dimensions
        }
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }