"""
main.py
Main entry point for AI Engine - Nigeria Tax Reform Bills Q&A Assistant
"""

import sys
from pathlib import Path

from .config import config
from .document_processor import load_and_chunk_documents
from .vector_store import VectorStore, initialize_vector_store
from .agent import TaxQAAgent, create_agent
from .utils import setup_logger, Timer


logger = setup_logger("main", config.LOG_FILE, config.LOG_LEVEL)


def initialize_system(reset_db: bool = False):
    """Initialize the complete AI Engine system"""
    logger.info("="*60)
    logger.info("INITIALIZING AI ENGINE")
    logger.info("="*60)
    
    logger.info("\n📚 Step 1: Loading documents...")
    with Timer() as t:
        chunks = load_and_chunk_documents()
    
    if not chunks:
        logger.error("❌ No documents found! Add PDFs to ./documents/")
        sys.exit(1)
    
    logger.info(f"✅ Loaded {len(chunks)} chunks in {t.elapsed():.2f}s")
    
    logger.info("\n🗄️ Step 2: Initializing vector store...")
    with Timer() as t:
        store = initialize_vector_store(chunks, reset=reset_db)
    
    logger.info(f"✅ Vector store ready in {t.elapsed():.2f}s")
    
    logger.info("\n🤖 Step 3: Creating AI agent...")
    with Timer() as t:
        agent = create_agent(store)
    
    logger.info(f"✅ Agent created in {t.elapsed():.2f}s")
    
    stats = store.get_collection_stats()
    logger.info("\n📊 System Statistics:")
    logger.info(f"   Documents: {stats['total_documents']}")
    logger.info(f"   Model: {config.LLM_MODEL}")
    logger.info(f"   Embeddings: {config.EMBEDDING_MODEL}")
    
    logger.info("\n✅ SYSTEM READY!")
    logger.info("="*60 + "\n")
    
    return agent, store


def demo_conversation(agent: TaxQAAgent):
    """Run a demo conversation"""
    print("\n" + "="*60)
    print("DEMO CONVERSATION")
    print("="*60 + "\n")
    
    session_id = "demo_session"
    
    test_queries = [
        "Hello! Can you help me understand the tax reform?",
        "Will I pay more income tax under the new law?",
        "What about small businesses?",
        "How does VAT distribution work?",
        "Thank you!"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*60}")
        print(f"Query {i}: {query}")
        print(f"{'─'*60}")
        
        with Timer() as t:
            response = agent.chat(query, session_id)
        
        print(f"\n🤖 Assistant:")
        print(response['response'])
        
        if response.get('sources'):
            print(f"\n📚 Sources ({len(response['sources'])}):")
            for j, source in enumerate(response['sources'][:2], 1):
                print(f"   {j}. {source['document']}")
        
        print(f"\n⏱️ Response time: {t.elapsed():.2f}s")


def interactive_mode(agent: TaxQAAgent):
    """Start interactive chat mode"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nAsk questions about Nigeria's Tax Reform Bills!")
    print("Type 'quit' to exit, 'clear' to reset session")
    print("="*60 + "\n")
    
    session_id = "interactive_session"
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'clear':
                agent.clear_session(session_id)
                print("✅ Session cleared!")
                continue
            
            with Timer() as t:
                response = agent.chat(query, session_id)
            
            print(f"\n🤖 Assistant: {response['response']}")
            
            if response.get('sources'):
                print(f"\n📚 Sources:")
                for source in response['sources'][:2]:
                    print(f"   • {source['document']}")
            
            print(f"\n⏱️ {t.elapsed():.2f}s")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        NIGERIA TAX REFORM BILLS Q&A ASSISTANT            ║
    ║              AI Engine - Samuel Dasaolu                  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    docs_path = Path(config.DOCS_DIRECTORY)
    if not docs_path.exists() or not list(docs_path.rglob("*.pdf")):
        print("⚠️  WARNING: No documents found!")
        print(f"   Add PDFs to: {config.DOCS_DIRECTORY}\n")
    
    try:
        agent, store = initialize_system(reset_db=False)
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)
    
    print("\nChoose mode:")
    print("  1. Run demo conversation")
    print("  2. Interactive mode")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_conversation(agent)
    elif choice == "2":
        interactive_mode(agent)
    else:
        print("👋 Goodbye!")
    
    print("\n" + "="*60)
    print("Thank you for using the Tax Reform Q&A Assistant!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()