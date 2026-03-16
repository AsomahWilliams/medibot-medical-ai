# app/api/upload_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload_service import upload_pdf, delete_from_pinecone, check_index_status
import os
import shutil

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/pdfs/")
async def upload_pdfs(file: UploadFile = File(...)):
    """Upload PDF file to Pinecone"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("./uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"./uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to Pinecone
        result = upload_pdf(file_path, source=file.filename)
        
        # Clean up
        os.remove(file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get Pinecone index status"""
    return check_index_status()