
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from fastapi import UploadFile, File
from app.services.vectorstore_service import load_vectorstore_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/upload-docs")
async def admin_upload_pdfs(files: List[UploadFile] = File(...)):
    """Admin upload - for Ghana Health Service documents
    
    These documents will be available to ALL users.
    Use this to upload Ghana Health Service PDFs about
    hypertension and kidney disease.
    """
    try:
        result = await load_vectorstore_admin(files)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
