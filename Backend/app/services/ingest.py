import json
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.database import get_es_client, init_es_indices
from app.core.parser import LogParserEngine  # Import your Phase 2 parsing engine

class DataSeederPipeline:
    def __init__(self):
        self.es = get_es_client()
        self.ai = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.index_name = "client_footprints"
        self.embedding_model = "gemini-embedding-2"
        # Initialize the parsing chunker
        self.parser = LogParserEngine(chunk_size=300, chunk_overlap=30)

    def _generate_vector(self, text: str) -> list:
        try:
            response = self.ai.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Failed to generate embedding: {e}")
            raise e

    def seed_sandbox_environment(self, synthetic_tickets_json: str):
        init_es_indices()
        tickets = json.loads(synthetic_tickets_json)
        print(f"Beginning fragmented hybrid vector seeding...")

        for ticket in tickets:
            raw_text = ticket.get("text", "")
            
            # Phase 2 Goal: Split long text strings into traceable semantic chunks
            text_chunks = self.parser.split_text(raw_text)
            
            for sub_idx, chunk in enumerate(text_chunks):
                content_vector = self._generate_vector(chunk)
                
                payload = {
                    "account_id": ticket.get("account_id", "cust_enterprise_01"),
                    "doc_type": "unstructured_log",
                    "text": chunk,                       # Chunked text supporting legacy mappings
                    "content": chunk,                    # Chunked text supporting hybrid queries
                    "content_vector": content_vector,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": ticket.get("source", "support_portal"),
                    "log_level": ticket.get("log_level", "ERROR"),
                    "chunk_id": sub_idx                  # Explicitly tracks trace fragments
                }
                
                self.es.index(index=self.index_name, document=payload)
                
        print("✅All documents safely tokenized, chunked, and vectorized.")
        
        
# Quick mock trigger block to test your ingestion directly
if __name__ == "__main__":
    # Feel free to paste your raw 30-ticket JSON block here or hook it up to your generator function!
    sample_data = """[
        {
            "account_id": "cust_enterprise_01",
            "text": "CRITICAL: Database connection timeout error on cluster-01. Hex error signature 0xDEADBEEF.",
            "source": "kubernetes_pod_logs",
            "log_level": "CRITICAL"
        }
    ]"""
    
    seeder = DataSeederPipeline()
    seeder.seed_sandbox_environment(sample_data)