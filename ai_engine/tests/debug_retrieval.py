"""
debug_retrieval.py
Diagnostic script to check raw similarity scores without threshold filtering.
"""
import sys
import os


from ai_engine.vector_store import VectorStore
from ai_engine.config import config

def diagnose():
    print("DIAGNOSTIC MODE: Checking Raw Scores")
    
    try:
        store = VectorStore()
        store.create_collection()
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return

    query = "companies income tax"
    print(f"\nQuery: '{query}'")
    
    embedding = store.embeddings.embed_query(query)
    
    results = store.collection.query(
        query_embeddings=[embedding],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\nTop 10 Raw Results (Threshold is {config.SIMILARITY_THRESHOLD}):")
    
    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            distance = results['distances'][0][i]
            score = 1 - distance
            
            doc_preview = results['documents'][0][i][:100].replace('\n', ' ')
            source = results['metadatas'][0][i].get('source', 'Unknown')
            
            status = "KEEP" if score >= config.SIMILARITY_THRESHOLD else "DROP"
            
            print(f"{i+1}. [{status}] Score: {score:.4f} | Source: {source}")
            print(f"   Preview: {doc_preview}...")
            print("-" * 50)
    else:
        print("Chroma returned NO results at all. Database might be empty?")

if __name__ == "__main__":
    diagnose()