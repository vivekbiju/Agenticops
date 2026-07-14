# Location: backend/app/core/database.py
import datetime
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from google import genai
from google.genai import types
from app.core.config import settings

def get_es_client() -> Elasticsearch:
    return Elasticsearch(settings.ELASTICSEARCH_URL)

def init_es_indices():
    es = get_es_client()
    index_name = "client_footprints"
    
    # Combined Phase 1 & Phase 2 Mappings Schema Layout
    mappings_schema = {
        "properties": {
            # Shared Metadata & Phase 1 Core Fields
            "account_id": {"type": "keyword"},
            "doc_type": {"type": "keyword"},  # 'metric_snapshot' or 'unstructured_log'
            "created_at": {"type": "date", "format": "yyyy-MM"},
            "mrr": {"type": "float"},
            "renewal_anniversary": {"type": "date"},
            "text": {"type": "text"},
            
            # Phase 2 Dense Vector & Hybrid Search Fields
            "timestamp": {"type": "date"},
            "source": {"type": "keyword"},
            "log_level": {"type": "keyword"},
            "chunk_id": {"type": "integer"},
            "content": { 
                "type": "text",
                "analyzer": "standard"
            },
            "content_vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
    
    try:
        # Directly try creating using the modern 8.x mappings keyword parameter
        es.indices.create(index=index_name, mappings=mappings_schema)
        print(f"Successfully initialized hybrid structural index: {index_name}")
    except Exception as e:
        error_str = str(e)
        if "resource_already_exists_exception" in error_str or "already_exists" in error_str:
            print(f"Index '{index_name}' already exists. Skipping initialization.")
        else:
            raise e

def seed_database_mock_records():
    """
    Retrieves real embeddings from gemini-embedding-2 and populates the 
    local Elasticsearch instance with structured historical log records.
    """
    es = get_es_client()
    index_name = "client_footprints"
    
    # Check if we already have mock logs seeded
    res = es.count(index=index_name)
    if res.get("count", 0) > 0:
        print(f"Index '{index_name}' is already populated with {res['count']} documents. Skipping seed.")
        return

    print("Generating vector embeddings using google-genai client...")
    ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Sample unstructured contextual system log messages to seed
    mock_logs = [
        "High latency spikes observed on database connection pool following cluster rotation.",
        "Fatal NullPointerException on transaction process coordinator service during checkouts.",
        "API Gateway reporting 504 gateway timeout on historical payment verification microservice."
    ]

    for idx, log_text in enumerate(mock_logs):
        try:
            # Leverage the google-genai modern embed endpoint
            emb_res = ai_client.models.embed_content(
                model="gemini-embedding-2",
                contents=log_text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            # Extract vector elements
            vector = emb_res.embeddings[0].values
            
            # Format and index the document into Elasticsearch
            doc = {
                "account_id": "acc_2026_99x",
                "doc_type": "unstructured_log",
                "created_at": "2026-07",
                "text": log_text,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": "syslog-collector-v2",
                "log_level": "ERROR" if "Fatal" in log_text else "WARNING",
                "chunk_id": idx + 1,
                "content": log_text,
                "content_vector": vector
            }
            
            es.index(index=index_name, document=doc, refresh=True)
            print(f"-> Indexed mock log fragment {idx + 1}/{len(mock_logs)} successfully!")
        except Exception as e:
            print(f"⚠️ Failed to generate embedding or index document: {str(e)}")

if __name__ == "__main__":
    print("\n====================================================================")
    print("🚀 Running Database Setup Script (app/core/database.py)")
    print("====================================================================")
    
    # Initialize index schema
    init_es_indices()
    
    # Seed index with vector data
    seed_database_mock_records()
    
    print("====================================================================\n")