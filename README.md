

# 🏥 MediBot - Medical AI Assistant

Specialized in **Hypertension & Kidney Disease in Ghana** using **RAG (Retrieval-Augmented Generation)**.

## 🎯 Features

- 🗣️ **AI Chat** powered by OpenRouter LLM
- 📚 **Ghana Health Service** document integration
- 🗃️ **Pinecone** vector database for semantic search
- 📤 **PDF Upload** for new medical documents
- 👤 **User Authentication** (Login/Signup)
- ⭐ **Feedback System** for continuous improvement
- 🛡️ **Rate Limiting** for security
- 📊 **Admin Dashboard** for statistics

## 🏗️ Architecture





┌────────────────────────────────────┐
│           FASTAPI BACKEND          │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ Authentication Service        │  │
│  │ - Login / Signup              │  │
│  │ - JWT Token Validation        │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │ Chat Controller (API Layer)  │  │
│  │ - Request validation         │  │
│  │ - Intent detection           │  │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  ┌──────────────▼───────────────┐  │
│  │     RAG Service Layer        │  │
│  │                               │ │
│  │ 1. Load User Question         │ │
│  │ 2. Create Embedding           │ │
│  │ 3. Vector Search              │ │
│  │ 4. Context Injection          │ │
│  └──────────────┬───────────────┘  │
│                 │                  │
│  └──────────────▼───────────────┘  │
│        LLM Service                 │
│   (OpenAI / Local Model)           │
└─────────────┬──────────────────────┘
│
▼
┌──────────────────────────┐
│       VECTOR DATABASE     │
│        (Pinecone)         │
│ - Ghana Health Chunks     │
│ - Embedded Vectors        │
└─────────────┬────────────┘
│
▼
┌──────────────────────────┐
│   KNOWLEDGE STORAGE       │
│                            │
│ Ghana Health Data Files    │
│ (PDF / TXT / Docs)         │
│                            │
│ PyLoader → Chunking →      │
│ Embedding Pipeline         │
└──────────────────────────┘


┌──────────────────────────┐
│        DATABASE           │
│       (PostgreSQL)        │
│ - Users                    │
│ - Chat History             │
│ - Sessions                 │
└──────────────────────────┘


RAG FLOW


User Question
↓
Embedding Model
↓
Vector Search (Pinecone)
↓
Relevant Health Chunks Retrieved
↓
Added to AI Prompt


Knowledge Pipeline offline process


Ghana Health Documents
↓
PyLoader
↓
Chunking
↓
Sentence Transformer Embedding
↓
Stored in Pinecone


DATA FLOW DIAGRAM


┌──────────────────────┐
│        USER           │
│  Web / Mobile Client  │
└──────────┬───────────┘
│
│ 1. Message Request
▼
┌──────────────────────────────┐
│        FASTAPI BACKEND        │
│  /chat endpoint               │
└──────────┬───────────────────┘
│
│ 2. Input Processing
▼
┌──────────────────────────────┐
│ Security & Validation Layer   │
│ - clean_input()               │
│ - emergency detection         │
│ - intent detection            │
│ - safety checks               │
└──────────┬───────────────────┘
│
│ 3. User & Session Check
▼
┌──────────────────────────────┐
│        PostgreSQL             │
│ - Users                       │
│ - Sessions                    │
│ - Chat history                │
└──────────┬───────────────────┘
│
│ 4. Query Embedding
▼
┌──────────────────────────────┐
│   Embedding Model             │
│ (Sentence Transformer)        │
│ Converts text → vector        │
└──────────┬───────────────────┘
│
│ 5. Semantic Search
▼
┌──────────────────────────────┐
│        Vector DB (Pinecone)   │
│ - Stored chunks               │
│ - Health knowledge vectors    │
└──────────┬───────────────────┘
│
│ 6. Retrieved Context
▼
┌──────────────────────────────┐
│        RAG Layer              │
│ Combine:                      │
│ - User question               │
│ - Retrieved medical context   │
└──────────┬───────────────────┘
│
│ 7. AI Generation
▼
┌──────────────────────────────┐
│        LLM (OpenAI API)       │
│ Generates safe response       │
└──────────┬───────────────────┘
│
│ 8. Output Safety Filter
▼
┌──────────────────────────────┐
│ Response Validation Layer     │
│ - Medical safety filtering    │
└──────────┬───────────────────┘
│
│ 9. Save Conversation
▼
┌──────────────────────────────┐
│        PostgreSQL             │
│ Store chat history            │
└──────────┬───────────────────┘
│
▼
┌──────────────────────┐
│        USER           │
│   AI Response         │
└──────────────────────┘


PROJECT FILES STRUCTURE


medical_ai/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth_routes.py          # Login/Signup
│   │   ├── chat_routes.py          # Chat endpoint
│   │   └── admin_routes.py         # Admin upload
│   │
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── rate_limiter.py         # Rate limiting
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py           # LLM chain
│   │   ├── retriever.py            # Vector search
│   │   ├── vectorstore_service.py  # Document storage
│   │   ├── intent_service.py       # Intent detection
│   │   ├── evaluation_service.py   # Logging
│   │   ├── chunking_service.py     # Text splitting
│   │   └── prompt_service.py       # Prompt templates
│   │
│   └── main.py                     # FastAPI app
│
├── frontend/
│   └── app.py                      # Streamlit UI
│
├── .env                            # API keys
├── requirements.txt                # Dependencies
└── evaluation_logs.jsonl           # Interaction logs




HOW TO RUN
# Terminal 1: Backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
source venv/bin/activate
streamlit run frontend/app.py


# Replace with your GitHub repo URL
git remote add origin https://github.com/YOUR_USERNAME/medibot-medical-ai.git

# Push to GitHub
git branch -M main
git push -u origin main
