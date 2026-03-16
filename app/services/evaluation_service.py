
"""
Evaluation Logging Service
Logs user interactions for evaluation and metrics
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class EvaluationLogger:
    """Logger for user interactions and evaluation metrics"""
    
    def __init__(self, log_file: str = "evaluation_logs.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename=str(self.log_file).replace(".jsonl", ".log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_interaction(
        self,
        user_id: Optional[str],
        question: str,
        intent: str,
        disease_scope: Dict,
        context_found: bool,
        response_length: int,
        response_time: float,
        sources: list,
        user_feedback: Optional[str] = None
    ):
        """
        Log a user interaction
        
        Args:
            user_id: User identifier (None for anonymous)
            question: User question
            intent: Detected intent
            disease_scope: Disease scope detection result
            context_found: Whether context was found
            response_length: Length of response
            response_time: Time taken to respond
            sources: Source documents used
            user_feedback: Optional user feedback
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id or "anonymous",
            "question": question,
            "intent": intent,
            "disease_scope": disease_scope,
            "context_found": context_found,
            "response_length": response_length,
            "response_time_seconds": round(response_time, 3),
            "sources_count": len(sources),
            "sources": sources,
            "user_feedback": user_feedback
        }
        
        # Write to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Log to console
        self.logger.info(
            f"Interaction: user={user_id or 'anonymous'}, "
            f"intent={intent}, context={context_found}, "
            f"time={response_time:.2f}s"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Calculate evaluation metrics from logs
        
        Returns:
            Dictionary of metrics
        """
        try:
            with open(self.log_file, "r") as f:
                logs = [json.loads(line) for line in f if line.strip()]
            
            if not logs:
                return {"total_interactions": 0}
            
            total = len(logs)
            context_found = sum(1 for l in logs if l.get("context_found", False))
            avg_response_time = sum(l["response_time_seconds"] for l in logs) / total
            
            # Intent distribution
            intent_counts = {}
            for log in logs:
                intent = log.get("intent", "unknown")
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            # Disease scope distribution
            disease_counts = {"hypertension": 0, "kidney": 0, "other": 0}
            for log in logs:
                scope = log.get("disease_scope", {})
                if scope.get("hypertension"):
                    disease_counts["hypertension"] += 1
                elif scope.get("kidney"):
                    disease_counts["kidney"] += 1
                else:
                    disease_counts["other"] += 1
            
            return {
                "total_interactions": total,
                "context_found_rate": round(context_found / total, 3),
                "avg_response_time_seconds": round(avg_response_time, 3),
                "intent_distribution": intent_counts,
                "disease_distribution": disease_counts,
                "unique_users": len(set(l["user_id"] for l in logs))
            }
            
        except FileNotFoundError:
            return {"total_interactions": 0, "message": "No logs found"}
    
    def clear_logs(self):
        """Clear all logs"""
        if self.log_file.exists():
            self.log_file.unlink()
        self.logger.info("Logs cleared")


# Global logger instance
evaluation_logger = EvaluationLogger()
