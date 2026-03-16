# app/services/retriever.py
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

def get_retriever(filter_metadata: Optional[Dict[str, Any]] = None):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    index_name = os.getenv("PINECONE_INDEX_NAME", "medicalindex")
    
    vectorstore = Pinecone.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )
    
    # Reduced k for faster search
    search_kwargs = {
        "k": 1,  # Reduced from 2 to 1
    }
    
    if filter_metadata:
        search_kwargs["filter"] = filter_metadata
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs
    )
    
    return retriever