# app/services/query_service.py

from app.services.ai_service import get_llm_chain


def query_chain(chain, question):
    """Query the LLM chain"""
    try:
        # FIX: Use .invoke() instead of calling as a function
        result = chain.invoke(question)
        
        return {
            "response": result,
            "sources": [],
            "source_documents": []
        }
    except Exception as e:
        print(f"Error in query_chain: {e}")
        return {
            "response": f"Error: {str(e)}",
            "sources": [],
            "source_documents": []
        }