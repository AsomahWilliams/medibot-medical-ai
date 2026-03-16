# ============================================
# IMPORTS
# ============================================
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.services.ai_service import get_llm_chain, get_retriever, is_within_scope
from app.services.query_service import query_chain
from app.services.intent_service import analyze_question, detect_disease_scope
from app.services.evaluation_service import evaluation_logger
from app.middlewares.rate_limiter import rate_limiter
import time

# ============================================
# ROUTER SETUP
# ============================================
router = APIRouter(prefix="/chat", tags=["Chat"])

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: list
    intent: str
    disease_scope: dict

# ============================================
# TEST ENDPOINT
# ============================================
@router.get("/test")
def test_chat():
    return {"message": "Chat route working"}

# ============================================
# ASK QUESTION ENDPOINT
# ============================================
@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: Request, chat_request: ChatRequest):
    start_time = time.time()
    
    # Check rate limit
    client_id = request.client.host
    is_allowed, remaining, reset_time = rate_limiter.check_rate_limit(client_id)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={"error": "Too many requests", "retry_after": reset_time}
        )
    
    try:
        user_input = chat_request.message
        
        # Analyze question
        analysis = analyze_question(user_input)
        disease_scope = analysis["disease_scope"]
        
        # Check if question is in scope
        if not disease_scope["in_scope"]:
            return ChatResponse(
                response="I'm MediBot, specialized in hypertension and kidney disease. Please ask about these topics.",
                sources=[],
                intent=analysis["intent"],
                disease_scope=disease_scope
            )
        
        # Get retriever and chain
        retriever = get_retriever()
        chain = get_llm_chain(retriever)
        
        # Get response
        result = query_chain(chain, user_input)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log interaction
        evaluation_logger.log_interaction(
            user_id=None,
            question=user_input,
            intent=analysis["intent"],
            disease_scope=disease_scope,
            context_found=len(result.get("source_documents", [])) > 0,
            response_length=len(result.get("response", "")),
            response_time=response_time,
            sources=result.get("sources", [])
        )
        
        return ChatResponse(
            response=result.get("response", "No response"),
            sources=result.get("sources", []),
            intent=analysis["intent"],
            disease_scope=disease_scope
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# METRICS ENDPOINT
# ============================================
@router.get("/metrics")
def get_metrics():
    return evaluation_logger.get_metrics()