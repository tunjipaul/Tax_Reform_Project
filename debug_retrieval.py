"""
debug_retrieval.py
Diagnostic script to check raw similarity scores without threshold filtering.
"""
import sys
import os

# Ensure we can import from ai_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.vector_store import VectorStore
from ai_engine.config import config

def diagnose():
    print("🔍 DIAGNOSTIC MODE: Checking Raw Scores")
    
    # Initialize store
    try:
        store = VectorStore()
        store.create_collection() # Connects to existing
    except Exception as e:
        print(f"❌ Failed to connect to DB: {e}")
        return

    # The failing query
    query = "companies income tax"
    print(f"\nQuery: '{query}'")
    
    # Manually run query to bypass the filtering in similarity_search
    # We need to access the store's internal methods or modify similarity_search
    # But wait, similarity_search prints DEBUG logs for discarded docs!
    
    # Let's run the existing method but look closely at the output
    # If the previous output showed NO debug logs, it means NOTHING was returned by Chroma even before filtering?
    # No, Chroma always returns k results.
    
    # Let's use the lower-level access to be sure.
    embedding = store.embeddings.embed_query(query)
    
    results = store.collection.query(
        query_embeddings=[embedding],
        n_results=10, # Get top 10
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n📊 Top 10 Raw Results (Threshold is {config.SIMILARITY_THRESHOLD}):")
    
    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            distance = results['distances'][0][i]
            score = 1 - distance # Assuming cosine
            
            doc_preview = results['documents'][0][i][:100].replace('\n', ' ')
            source = results['metadatas'][0][i].get('source', 'Unknown')
            
            status = "✅ KEEP" if score >= config.SIMILARITY_THRESHOLD else "❌ DROP"
            
            print(f"{i+1}. [{status}] Score: {score:.4f} | Source: {source}")
            print(f"   Preview: {doc_preview}...")
            print("-" * 50)
    else:
        print("❌ Chroma returned NO results at all. Database might be empty?")

if __name__ == "__main__":
    diagnose()