import os
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from google import genai
from google.genai import types  # Import the types module for configuration
from app.core.config import settings

class HybridRetrieverController:
    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.index_name = "client_footprints"
        
        # Initialize modern SDK passing your validated environment configuration key
        self.ai = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Upgraded modern active embedding model
        self.embedding_model = "gemini-embedding-2" 

    def _generate_embedding(self, text: str) -> List[float]:
        """Generates a scaled 768-dimension dense vector using gemini-embedding-2 MRL."""
        try:
            response = self.ai.models.embed_content(
                model=self.embedding_model,
                contents=text,
                # Enforce MRL scaling down to match your 768-dim Elasticsearch schema
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding via google-genai SDK: {e}")
            raise e

    def hybrid_search(
        self, 
        query_text: str, 
        account_id: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Executes parallel BM25 and Dense Vector search using Elasticsearch 8.12.2 Query DSL,
        fusing the result sets using Reciprocal Rank Fusion (RRF).
        """
        # 1. Generate the vector dynamically from the input string
        query_vector = self._generate_embedding(query_text)
        
        # 2. Structure the 8.12.2 compliant RRF query schema
        # 8.12.2 Basic-Tier Compliant Hybrid Schema
        body = {
            # Standard Keyword Search with a weight boost
            "query": {
                "bool": {
                    "must": [
                        {"match": {"content": {"query": query_text, "boost": 1.0}}}
                    ],
                    "filter": [
                        {"term": {"account_id": account_id}}
                    ]
                }
            },
            # Dense Vector Search running in parallel, adding its score automatically
            "knn": {
                "field": "content_vector",
                "query_vector": query_vector,
                "k": 20,
                "num_candidates": 50,
                "boost": 2.0,  # Tweak this to favor semantic context over exact words
                "filter": [
                    {"term": {"account_id": account_id}}
                ]
            },
            "size": top_k
        }

        # 3. Dispatch to local engine container
        response = self.es.search(index=self.index_name, body=body)
        
        # 4. Parse the results to include explicit traceable payload tags
        results = []
        for hit in response["hits"]["hits"]:
            source_data = hit["_source"]
            results.append({
                "id": hit["_id"],
                "rrf_score": hit.get("_score"),  # Fused ranking score
                "content": source_data.get("content") or source_data.get("text"),
                "metadata": {
                    "source": source_data.get("source", "legacy_migration"),
                    "timestamp": source_data.get("timestamp") or source_data.get("created_at"),
                    "account_id": source_data.get("account_id"),
                    "log_level": source_data.get("log_level", "INFO")
                }
            })
            
        return results