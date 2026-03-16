
"""
Prompt Service
Manages prompt templates for the chatbot
"""

from langchain_core.prompts import PromptTemplate


# Main medical prompt
MEDICAL_PROMPT = """You are MediBot, a medical assistant specialized in hypertension and kidney disease in Ghana.

## Instructions
- Answer based ONLY on the provided context
- If context doesn't have relevant information, use your general medical knowledge
- Be educational and informative
- Do NOT provide diagnosis or prescription
- Keep answers concise (2-3 paragraphs)
- Use clear, simple language

## Context
{context}

## Question
{question}

## Answer
"""

# Fallback prompt when no context
FALLBACK_PROMPT = """You are MediBot, a medical assistant specialized in hypertension and kidney disease in Ghana.

## Instructions
- Answer based on your general medical knowledge
- Be educational and informative
- Do NOT provide diagnosis or prescription
- Keep answers concise (2-3 paragraphs)
- If unsure, recommend consulting a healthcare professional

## Question
{question}

## Answer
"""

# Scope restriction message
SCOPE_MESSAGE = """I'm MediBot, specialized in:

- Hypertension (High Blood Pressure)
- Kidney Disease

Please ask questions about these TWO topics only.

⚠️ No diagnosis or prescription."""


def get_medical_prompt() -> PromptTemplate:
    """Get the main medical prompt template"""
    return PromptTemplate(
        input_variables=["context", "question"],
        template=MEDICAL_PROMPT
    )


def get_fallback_prompt() -> PromptTemplate:
    """Get the fallback prompt template"""
    return PromptTemplate(
        input_variables=["question"],
        template=FALLBACK_PROMPT
    )


def get_scope_message() -> str:
    """Get the scope restriction message"""
    return SCOPE_MESSAGE
