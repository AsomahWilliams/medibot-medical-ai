# ============================================
# IMPORTS
# ============================================
import os
import logging
import time
import re
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings

# ============================================
# FIX TOKENIZERS WARNING
# ============================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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
# ALLOWED KEYWORDS (Medical Topics) - UPDATED
# ============================================
ALLOWED_KEYWORDS = [

# ------------------------------------------------
# DISEASE NAMES
# ------------------------------------------------
"hypertension","high blood pressure","blood pressure","bp","hbp",
"hypertensive","arterial pressure","systolic pressure","diastolic pressure",

"kidney","renal","kidney disease","kidney failure","renal failure",
"chronic kidney disease","ckd","acute kidney injury","aki",
"kidney disorder","kidney condition","kidney damage","renal disease",

# ------------------------------------------------
# SYMPTOMS
# ------------------------------------------------
"symptom","symptoms","sign","signs","warning signs",

"headache","severe headache","dizziness","lightheadedness",
"fatigue","tiredness","confusion","blurred vision","vision problems",
"nosebleeds","chest pain","shortness of breath",

"swelling","edema","fluid retention","leg swelling","ankle swelling",
"face swelling","puffy eyes",

"nausea","vomiting","loss of appetite","metallic taste",

"frequent urination","urination","urine","foamy urine",
"blood in urine","dark urine","painful urination",

"kidney pain","back pain","flank pain",

# ------------------------------------------------
# RISK FACTORS
# ------------------------------------------------
"risk","risk factor","risk factors","risk of",

"age","aging","old age",
"genetics","genetic","hereditary","family history",
"ethnicity",

"obesity","overweight","body weight",
"smoking","tobacco",
"alcohol","drinking",
"stress","chronic stress",

"diabetes","high blood sugar","insulin resistance",
"heart disease","cardiovascular disease",
"high cholesterol",

"sedentary lifestyle","lack of exercise","physical inactivity",

"poor diet","high salt diet","high sodium diet","junk food",

# ------------------------------------------------
# CAUSES
# ------------------------------------------------
"cause","causes","what causes","why does",
"primary hypertension","secondary hypertension",

"kidney infection","glomerulonephritis",
"polycystic kidney disease",
"lupus kidney disease",

"urinary obstruction",
"kidney stones",

# ------------------------------------------------
# DIAGNOSIS
# ------------------------------------------------
"diagnosis","diagnose","detection","screening",
"medical test","tests","testing",

"blood pressure test","blood pressure reading",
"systolic","diastolic",

"urine test","urinalysis",
"blood test",

"creatinine","serum creatinine",
"glomerular filtration rate","gfr","egfr",

"albumin","albuminuria","proteinuria",
"microalbumin",

"kidney biopsy",
"kidney ultrasound",
"ct scan","mri scan",

# ------------------------------------------------
# STAGES
# ------------------------------------------------
"stage","stages",
"stage 1 ckd","stage 2 ckd","stage 3 ckd","stage 4 ckd","stage 5 ckd",
"end stage kidney disease","eskd","end stage renal disease","esrd",

"hypertension stage 1","hypertension stage 2","hypertensive crisis",

# ------------------------------------------------
# COMPLICATIONS
# ------------------------------------------------
"complication","complications",

"heart attack","stroke",
"heart failure",

"kidney failure",
"cardiovascular disease",

"vision loss","retinopathy",
"nerve damage","neuropathy",

"fluid overload",

# ------------------------------------------------
# TREATMENT
# ------------------------------------------------
"treatment","treat","therapy","management",
"manage","control","medical care",

"dialysis","hemodialysis","peritoneal dialysis",
"kidney transplant",

"lifestyle change","lifestyle modification",

# ------------------------------------------------
# MEDICATIONS
# ------------------------------------------------
"medication","medicine","drug","drugs",

"ace inhibitors","angiotensin converting enzyme inhibitors",
"arbs","angiotensin receptor blockers",
"beta blockers",
"calcium channel blockers",
"diuretics","water pills",

"antihypertensive drugs",

# ------------------------------------------------
# PREVENTION
# ------------------------------------------------
"prevent","prevention","preventing",

"early detection","screening",

"healthy lifestyle",

# ------------------------------------------------
# DIET
# ------------------------------------------------
"diet","nutrition","foods","food",

"low salt diet","low sodium diet",
"dash diet",

"potassium intake",
"protein intake",
"fluid intake",
"water intake",

# ------------------------------------------------
# LIFESTYLE
# ------------------------------------------------
"exercise","physical activity","workout",

"weight loss","lose weight",

"sleep","sleep apnea",

"stress management",

# ------------------------------------------------
# MONITORING
# ------------------------------------------------
"monitor","monitoring",

"blood pressure monitor",
"home blood pressure monitor",

"kidney function test",

"lab results","lab values",

# ------------------------------------------------
# GENERAL QUESTIONS
# ------------------------------------------------
"what is","what are","how does","how to",
"can","should","is it safe","why",

"best way","how long","how often",
"when to see doctor",

]



# ============================================
# SCOPE MESSAGE (IMPROVED)
# ============================================
SCOPE_MESSAGE = """I'm MediBot, specialized in:

- Hypertension (High Blood Pressure)
- Kidney Disease

Please ask questions about these TWO topics only.

⚠️ No diagnosis or prescription.

Examples of valid questions:
- What are the risk factors for kidney disease?
- How to prevent hypertension?
- What are the symptoms of kidney disease?
- What causes high blood pressure?"""

# ============================================
# PINECONE CONFIGURATION
# ============================================
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medicalindex")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ============================================
# SCOPE CHECKING (IMPROVED)
# ============================================
def is_within_scope(question: str) -> bool:
    """Check if question is within allowed medical topics"""
    question_lower = question.lower()
    
    # Debug: Log the question and keywords
    logger.info(f"Checking scope for question: {question_lower}")
    
    # Check if any keyword matches
    matches = [kw for kw in ALLOWED_KEYWORDS if kw in question_lower]
    logger.info(f"Matching keywords: {matches}")
    
    return any(kw in question_lower for kw in ALLOWED_KEYWORDS)

# ============================================
# PINECONE RETRIEVER (IMPROVED)
# ============================================
def get_retriever(filter_metadata: Dict = None):
    """Get Pinecone retriever with error handling"""
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
        
        # IMPROVED: Lower threshold to get more results
        search_kwargs = {
            "k": 5,  # Get 5 relevant documents
            "score_threshold": 0.3,  # Lower threshold for better recall
        }
        
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata
        
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs=search_kwargs
        )
        
        logger.info(f"Pinecone retriever initialized successfully")
        return retriever
        
    except Exception as e:
        logger.error(f"Pinecone connection error: {str(e)}")
        raise e

# ============================================
# LLM CONFIGURATION
# ============================================
def get_llm():
    """Get OpenRouter LLM with proper configuration"""
    try:
        llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            temperature=0.3,
            max_tokens=500,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            request_timeout=45
        )
        return llm
    except Exception as e:
        logger.error(f"LLM initialization error: {str(e)}")
        raise e

# ============================================
# PROMPT TEMPLATE (UPDATED - GENERAL KNOWLEDGE + RESTRICTED)
# ============================================
def get_prompt_template():
    """Get prompt template for RAG"""
    return PromptTemplate(
        input_variables=["context", "question"],
        template="""You are MediBot, a medical AI assistant specialized in hypertension and kidney disease.

IMPORTANT RULES:
1. Answer ONLY about hypertension or kidney disease.
2. If the question is about any other disease or medical condition, politely refuse and say: "I am only specialized in hypertension and kidney disease. Please ask about those topics."
3. Do NOT provide diagnosis or prescription.
4. Use the context provided below if available.
5. If context is empty or not relevant, use your general medical knowledge to answer (but still only about hypertension or kidney disease).
6. Be clear, concise, and educational.
7. Always include a medical disclaimer at the end.
8. DO NOT output HTML tags like <div>, </div>, etc.

Context:
{context}

Question: {question}

Answer (in markdown format):"""
    )

# ============================================
# DOCUMENT FORMATTING (CLEANED - HTML REMOVED)
# ============================================
def format_docs(docs: List[Document]) -> str:
    """Format documents for context (removes HTML tags)"""
    if not docs:
        return "No relevant information available in our medical database."
    
    formatted_docs = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        
        # Remove HTML tags from page content
        page_content = doc.page_content
        page_content = re.sub(r'<[^>]+>', '', page_content)  # Remove HTML tags
        page_content = re.sub(r'\s+', ' ', page_content)     # Clean extra whitespace
        page_content = page_content.strip()
        
        formatted_docs.append(f"[{i}] Source: {source}\n{page_content}")
    
    return "\n\n".join(formatted_docs)

# ============================================
# SOURCE EXTRACTION
# ============================================
def extract_sources(docs: List[Document]) -> List[str]:
    """Extract source information from documents"""
    sources = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        if source not in sources:
            sources.append(source)
    return sources

# ============================================
# RESPONSE VALIDATION (CLEANED - HTML REMOVED)
# ============================================
def validate_response(response_text: str) -> str:
    """Validate and clean response (removes HTML tags)"""
    if not response_text:
        return "I apologize, but I couldn't generate a response at this time. Please try again."
    
    # Remove any remaining HTML tags
    response_text = re.sub(r'<[^>]+>', '', response_text)
    
    # Clean extra whitespace
    response_text = re.sub(r'\s+', ' ', response_text)
    
    response_text = response_text.strip()
    
    if len(response_text) < 20:
        return "I apologize, but I couldn't generate a comprehensive response. Please try again."
    
    return response_text

# ============================================
# LLM CHAIN CREATION
# ============================================
def get_llm_chain(retriever):
    """Create and return a LangChain RAG chain with retriever"""
    try:
        llm = get_llm()
        prompt = get_prompt_template()
        
        chain = (
            {"context": lambda x: retriever.invoke(x), "question": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("LLM chain created successfully with retriever")
        return chain
        
    except Exception as e:
        logger.error(f"LLM chain creation error: {str(e)}")
        raise e

# ============================================
# MAIN CHAT FUNCTION (IMPROVED)
# ============================================
def chat(message: str) -> Dict[str, Any]:
    """Main chat function with RAG pipeline"""
    start_time = time.time()
    
    try:
        if not message or len(message.strip()) == 0:
            return {
                "error": "Message cannot be empty",
                "sources": [],
                "intent": "error"
            }
        
        # Check scope
        in_scope = is_within_scope(message)
        logger.info(f"Question in scope: {in_scope}")
        
        if not in_scope:
            return {
                "response": SCOPE_MESSAGE,
                "sources": [],
                "intent": "out_of_scope"
            }
        
        retriever = get_retriever()
        docs = retriever.invoke(message)
        context = format_docs(docs)
        llm = get_llm()
        prompt = get_prompt_template()
        formatted_prompt = prompt.format(context=context, question=message)
        result = llm.invoke(formatted_prompt)
        
        if hasattr(result, 'content'):
            response_text = result.content
        else:
            response_text = str(result)
        
        # ✅ Double clean the response
        response_text = validate_response(response_text)
        
        sources = extract_sources(docs)
        processing_time = time.time() - start_time
        
        logger.info(f"Chat processed successfully - Time: {processing_time:.2f}s - Sources: {len(sources)}")
        
        return {
            "response": response_text,
            "sources": sources,
            "intent": "medical_question",
            "processing_time": processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Chat error: {str(e)}")
        logger.error(f"Processing time: {processing_time:.2f}s")
        
        return {
            "error": f"Error: {str(e)}",
            "sources": [],
            "intent": "error"
        }

# ============================================
# HEALTH CHECK
# ============================================
def health_check() -> Dict[str, Any]:
    """Check if AI services are healthy"""
    try:
        if not PINECONE_API_KEY:
            return {"status": "unhealthy", "service": "pinecone", "error": "API key not configured"}
        
        if not OPENROUTER_API_KEY:
            return {"status": "unhealthy", "service": "openrouter", "error": "API key not configured"}
        
        return {
            "status": "healthy",
            "services": {
                "pinecone": "connected",
                "openrouter": "connected"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ============================================
# RUN TEST
# ============================================
if __name__ == "__main__":
    test_message = "What is hypertension?"
    result = chat(test_message)
    print(f"Test Result: {result}")