"""
Rate Limiting
Simple rate limiter for chat endpoints
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RateLimiter:
    """Simple rate limiter for chat endpoints"""
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> Tuple[bool, int, int]:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            oldest = min(self.requests[client_id])
            reset_time = int(oldest + self.window_seconds - now)
            return False, 0, reset_time
        
        # Record request
        self.requests[client_id].append(now)
        
        remaining = self.max_requests - len(self.requests[client_id])
        return True, remaining, 60


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)