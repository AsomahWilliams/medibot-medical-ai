
"""
Streaming Service
Handles response streaming for real-time output
"""

from typing import Generator
import json


def stream_response(response_text: str, chunk_size: int = 50) -> Generator[str, None, None]:
    """
    Stream response text in chunks
    
    Args:
        response_text: Full response text
        chunk_size: Size of each chunk
    
    Yields:
        Text chunks for streaming
    """
    words = response_text.split()
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    yield f"data: {json.dumps({'chunk': '[END]'})}\n\n"


def format_stream_event(event_type: str, data: dict) -> str:
    """Format a streaming event"""
    return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"
