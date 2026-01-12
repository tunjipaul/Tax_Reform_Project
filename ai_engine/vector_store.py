"""
vector_store.py
Chroma vector database setup with Gemini embeddings
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from google import genai
from google.genai import types

from .config import config
from .document_processor import DocumentChunk


class GeminiEmbeddings:
    """Wrapper for Gemini embeddings using new SDK"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = []
        
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT"
                    )
                )
                
                batch_embeddings = [emb.values for emb in result.embeddings]
                embeddings.extend(batch_embeddings)
                
                print(f"Embedded batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            except Exception as e:
                print(f"Error embedding batch: {e}")
                embeddings.extend([[0.0] * 768 for _ in batch])
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY"
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Error embedding query: {e}")
            return [0.0] * 768


class VectorStore:
    """Manage Chroma vector database for tax reform documents"""
    
    def __init__(self):
        self.embeddings = GeminiEmbeddings(
            api_key=config.GEMINI_API_KEY,
            model=config.EMBEDDING_MODEL
        )
        
        self.client = chromadb.PersistentClient(
            path=config.VECTOR_STORE_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = config.COLLECTION_NAME
        self.collection = None
    
    def create_collection(self, reset: bool = False):
        """Create or get collection"""
        if reset:
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except Exception:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "description": "Nigeria Tax Reform Bills 2024", 
                "hnsw:space": "cosine"
            }
        )
        
        print(f"Collection ready: {self.collection_name}")
        return self.collection
    
    def add_documents(self, chunks: List[DocumentChunk]):
        """Add document chunks to vector store"""
        if not self.collection:
            self.create_collection()
        
        print(f"\nAdding {len(chunks)} chunks to vector store...")
        
        texts = [chunk.content for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        print("Generating embeddings...")
        embeddings = self.embeddings.embed_documents(texts)
        
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:end_idx],
                documents=texts[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
            print(f"Saved batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        print(f"All chunks added to vector store!")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        """
        if not self.collection:
            print("Collection not initialized!")
            return []
        
        k = k or config.RETRIEVAL_TOP_K
        
        query_embedding = self.embeddings.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict,
            include=["documents", "metadatas", "distances"]
        )
        
        documents = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                raw_distance = results['distances'][0][i]
                similarity_score = 1 - raw_distance
                
                print(f"   DEBUG: Doc {i} score: {similarity_score:.4f} (Threshold: {config.SIMILARITY_THRESHOLD})")

                doc = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": similarity_score,
                }
                
                if doc['score'] >= config.SIMILARITY_THRESHOLD:
                    documents.append(doc)
                else:
                    print(f"   Discarded Doc {i} (Score {similarity_score:.4f} < {config.SIMILARITY_THRESHOLD})")
        
        return documents
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        count = self.collection.count()
        
        return {
            "name": self.collection_name,
            "total_documents": count,
            "path": config.VECTOR_STORE_PATH,
            "embedding_model": config.EMBEDDING_MODEL
        }
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")


def initialize_vector_store(chunks: List[DocumentChunk], reset: bool = False) -> VectorStore:
    """Initialize vector store with documents"""
    store = VectorStore()
    store.create_collection(reset=reset)
    
    if chunks:
        store.add_documents(chunks)
    
    return store


def test_retrieval(store: VectorStore, query: str):
    """Test retrieval with a query"""
    print(f"\nTesting query: '{query}'")
    results = store.similarity_search(query, k=3)
    
    if results:
        print(f"\nFound {len(results)} relevant documents:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. Score: {doc['score']:.3f}")
            print(f"   Source: {doc['metadata'].get('source', 'Unknown')}")
            print(f"   Content: {doc['content'][:200]}...")
    else:
        print("No relevant documents found")


if __name__ == "__main__":
    from .document_processor import load_and_chunk_documents
    

    print("Loading and chunking documents...")
    chunks = load_and_chunk_documents()
    
    if not chunks:
        print("No documents to process. Add PDFs to ./documents/")
        exit(1)
    

    print("\nInitializing vector store...")
    store = initialize_vector_store(chunks, reset=True)
    

    test_queries = [
        "Will I pay more income tax?",
        "How does VAT derivation work?",
        "What happens to small businesses?"
    ]
    
    for query in test_queries:
        test_retrieval(store, query)
    

    print("\nCollection Statistics:")
    stats = store.get_collection_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")