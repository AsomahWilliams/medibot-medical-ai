
"""
Vector Store Service
Handles document storage with user namespaces
"""

from typing import List, Optional
from fastapi import UploadFile, HTTPException
import os
import tempfile
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()


async def load_vectorstore(
    files: List[UploadFile], 
    user_id: Optional[str] = None,
    doc_type: str = "user_upload"
):
    """
    Load documents to vector store with user namespace
    
    Args:
        files: List of PDF files
        user_id: User ID (None for admin/Ghana Health docs)
        doc_type: Type of document (ghana_health, user_upload)
    
    Returns:
        Success message
    """
    temp_dir = tempfile.mkdtemp()
    documents = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata["doc_type"] = doc_type
                doc.metadata["source"] = file.filename
                doc.metadata["filename"] = file.filename
                
                if user_id:
                    doc.metadata["user_id"] = user_id
            
            documents.extend(docs)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )
        split_docs = text_splitter.split_documents(documents)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Determine namespace
        if user_id:
            namespace = f"user_{user_id}"  # User-specific namespace
        else:
            namespace = "default"  # Admin/Ghana Health docs (available to all)

        Pinecone.from_documents(
            documents=split_docs,
            embedding=embeddings,
            index_name=os.getenv("PINECONE_INDEX_NAME", "medicalindex"),
            namespace=namespace
        )

        return {
            "message": f"Successfully processed {len(files)} files",
            "namespace": namespace,
            "doc_type": doc_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def load_vectorstore_admin(files: List[UploadFile]):
    """
    Admin upload - documents available to ALL users
    Uses default namespace
    """
    return await load_vectorstore(files, user_id=None, doc_type="ghana_health")
