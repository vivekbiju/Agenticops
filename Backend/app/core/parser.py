import uuid
from typing import List, Dict, Any
from datetime import datetime

class LogParserEngine:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """Simple sliding window word chunker."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
            if i + self.chunk_size >= len(words):
                break
        return chunks if chunks else [text]

    def build_payload(
        self, 
        text_chunk: str, 
        vector: List[float], 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assembles structured, traceable payload tags."""
        return {
            "account_id": metadata.get("account_id", "unknown_enterprise"),
            "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
            "source": metadata.get("source", "system_log_stream"),
            "log_level": metadata.get("log_level", "INFO"),
            "content": text_chunk,
            "content_vector": vector
        }