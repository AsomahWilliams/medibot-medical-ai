
"""
Intent Detection Service
Detects user intent from questions
"""

from enum import Enum
from typing import Dict, List


class Intent(Enum):
    """User intent types"""
    DEFINITION = "definition"
    SYMPTOMS = "symptoms"
    CAUSES = "causes"
    PREVENTION = "prevention"
    RISK_FACTORS = "risk_factors"
    TREATMENT = "treatment"
    DIAGNOSIS = "diagnosis"
    GENERAL = "general"
    UNKNOWN = "unknown"


# Intent keywords mapping
INTENT_KEYWORDS: Dict[Intent, List[str]] = {
    Intent.DEFINITION: [
        "what is", "what are", "define", "definition", "meaning",
        "explain", "describe", "what do you mean by"
    ],
    Intent.SYMPTOMS: [
        "symptom", "symptoms", "sign", "signs", "signs of",
        "how do i know", "what are the signs", "warning signs"
    ],
    Intent.CAUSES: [
        "cause", "causes", "what causes", "reason", "reasons",
        "why does", "lead to", "result in"
    ],
    Intent.PREVENTION: [
        "prevent", "prevention", "preventing", "how to prevent",
        "avoid", "stop", "reduce risk", "lower risk"
    ],
    Intent.RISK_FACTORS: [
        "risk factor", "risk factors", "who is at risk",
        "high risk", "predisposed", "vulnerable"
    ],
    Intent.TREATMENT: [
        "treatment", "treatments", "cure", "remedy", "manage",
        "how to treat", "therapy", "medication"
    ],
    Intent.DIAGNOSIS: [
        "diagnose", "diagnosis", "test", "screening", "check",
        "how to know", "identify"
    ],
    Intent.GENERAL: [
        "information", "info", "tell me about", "learn about"
    ]
}


# Disease keywords
HYPERTENSION_KEYWORDS = [
    "hypertension", "high blood pressure", "blood pressure",
    "bp", "heart pressure", "arterial pressure"
]

KIDNEY_KEYWORDS = [
    "kidney", "renal", "kidney disease", "kidney failure",
    "nephritis", "nephropathy"
]


def detect_intent(user_input: str) -> Intent:
    """
    Detect user intent from input
    
    Args:
        user_input: User question
    
    Returns:
        Detected intent
    """
    user_input_lower = user_input.lower()
    
    # Check each intent
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                return intent
    
    return Intent.UNKNOWN


def detect_disease_scope(user_input: str) -> Dict:
    """
    Detect which disease the question is about
    
    Args:
        user_input: User question
    
    Returns:
        Dictionary with disease detection results
    """
    user_input_lower = user_input.lower()
    
    has_hypertension = any(kw in user_input_lower for kw in HYPERTENSION_KEYWORDS)
    has_kidney = any(kw in user_input_lower for kw in KIDNEY_KEYWORDS)
    
    return {
        "hypertension": has_hypertension,
        "kidney": has_kidney,
        "in_scope": has_hypertension or has_kidney
    }


def analyze_question(user_input: str) -> Dict:
    """
    Full question analysis
    
    Args:
        user_input: User question
    
    Returns:
        Analysis results
    """
    return {
        "intent": detect_intent(user_input).value,
        "disease_scope": detect_disease_scope(user_input),
        "question": user_input,
        "length": len(user_input)
    }
