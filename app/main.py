# ============================================
# IMPORTS
# ============================================
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth_routes, chat_routes, upload_routes, admin_routes
from app.core.database import engine
from app.models.user import Base

# ============================================
# CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# LIFESPAN MANAGER
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting MediBot API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down MediBot API...")

# ============================================
# CREATE APP
# ============================================
app = FastAPI(
    title="MediBot Medical AI API",
    version="1.0.0",
    description="AI-powered medical assistant using RAG architecture",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================
# CORS MIDDLEWARE
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# INCLUDE ROUTERS (NO PREFIX HERE)
# ============================================
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(upload_routes.router)
app.include_router(admin_routes.router)

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MediBot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ============================================
# RUN APP
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=300
    )