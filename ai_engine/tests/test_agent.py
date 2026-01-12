"""
test_agent.py
Comprehensive test suite for the AI Engine

Run with: pytest tests/test_agent.py -v
"""

import pytest
from typing import List, Dict
import time

from agent import TaxQAAgent, create_agent
from vector_store import VectorStore
from document_processor import DocumentChunk
from memory import ConversationMemory


@pytest.fixture
def sample_chunks() -> List[DocumentChunk]:
    """Create sample document chunks for testing"""
    return [
        DocumentChunk(
            content="Income tax rates have been revised. Individuals earning below N800,000 are exempt from personal income tax.",
            metadata={
                "source": "Nigeria Tax Bill 2024",
                "section": "Section 12",
                "type": "pdf"
            },
            chunk_id="test_chunk_1"
        ),
        DocumentChunk(
            content="Small businesses with annual turnover below N50 million are exempt from company income tax.",
            metadata={
                "source": "Nigeria Tax Bill 2024",
                "section": "Section 45",
                "type": "pdf"
            },
            chunk_id="test_chunk_2"
        ),
        DocumentChunk(
            content="VAT distribution formula now allocates 60% derivation, 20% equality, 20% population.",
            metadata={
                "source": "Nigeria Tax Administration Bill 2024",
                "section": "Section 23",
                "type": "pdf"
            },
            chunk_id="test_chunk_3"
        )
    ]


@pytest.fixture
def vector_store(sample_chunks) -> VectorStore:
    """Initialize vector store with sample data"""
    store = VectorStore()
    store.create_collection(reset=True)
    store.add_documents(sample_chunks)
    return store


@pytest.fixture
def agent(vector_store) -> TaxQAAgent:
    """Create agent instance"""
    return create_agent(vector_store)


class TestGreetingHandling:
    """Test that greetings don't trigger retrieval"""
    
    def test_simple_greeting(self, agent):
        """Hello should not retrieve documents"""
        response = agent.chat(
            message="Hello",
            session_id="test_greeting"
        )
        
        assert response["retrieved"] == False
        assert len(response["response"]) > 0
        assert "hello" in response["response"].lower() or "hi" in response["response"].lower()
    
    def test_various_greetings(self, agent):
        """Test multiple greeting formats"""
        greetings = [
            "Hi there",
            "Good morning",
            "Hey",
            "Good afternoon"
        ]
        
        for greeting in greetings:
            response = agent.chat(greeting, "test_greetings")
            assert response["retrieved"] == False, f"Failed for: {greeting}"


class TestPolicyQuestions:
    """Test retrieval for policy-related questions"""
    
    def test_income_tax_question(self, agent):
        """Should retrieve for income tax questions"""
        response = agent.chat(
            message="Will I pay more income tax?",
            session_id="test_policy_1"
        )
        
        assert response["retrieved"] == True
        assert len(response["sources"]) > 0
        assert "income tax" in response["response"].lower()
    
    def test_vat_question(self, agent):
        """Should retrieve for VAT questions"""
        response = agent.chat(
            message="How does VAT distribution work?",
            session_id="test_policy_2"
        )
        
        assert response["retrieved"] == True
        assert len(response["sources"]) > 0
    
    def test_small_business_question(self, agent):
        """Should retrieve for business-related questions"""
        response = agent.chat(
            message="What happens to small businesses?",
            session_id="test_policy_3"
        )
        
        assert response["retrieved"] == True
        assert "small business" in response["response"].lower()


class TestConversationMemory:
    """Test conversation context and follow-ups"""
    
    def test_follow_up_uses_context(self, agent):
        """Follow-up questions should use conversation history"""
        session_id = "test_memory"
        
        response1 = agent.chat(
            "What is the income tax threshold?",
            session_id
        )
        
        response2 = agent.chat(
            "What if I earn more than that?",
            session_id
        )
        
        history = agent.get_conversation_history(session_id)
        assert len(history) >= 4
    
    def test_memory_persistence(self, agent):
        """Memory should persist across multiple messages"""
        session_id = "test_persistence"
        
        messages = [
            "Will I pay more tax?",
            "What about VAT?",
            "How does that affect Lagos?"
        ]
        
        for msg in messages:
            agent.chat(msg, session_id)
        
        history = agent.get_conversation_history(session_id)
        assert len(history) == len(messages) * 2


class TestCitations:
    """Test source citation functionality"""
    
    def test_citations_present(self, agent):
        """Policy answers should include citations"""
        response = agent.chat(
            "What is the income tax exemption threshold?",
            "test_citations"
        )
        
        if response["retrieved"]:
            assert len(response["sources"]) > 0
            
            source = response["sources"][0]
            assert "document" in source
            assert "excerpt" in source
            assert "score" in source
    
    def test_no_citations_for_greetings(self, agent):
        """Greetings shouldn't have citations"""
        response = agent.chat("Hello", "test_no_citations")
        
        assert response["retrieved"] == False
        assert len(response.get("sources", [])) == 0


class TestResponseQuality:
    """Test response accuracy and quality"""
    
    def test_response_not_empty(self, agent):
        """All responses should have content"""
        messages = [
            "Hello",
            "Will I pay more tax?",
            "Thank you"
        ]
        
        for msg in messages:
            response = agent.chat(msg, f"test_quality_{msg}")
            assert len(response["response"]) > 0
    
    def test_factual_accuracy(self, agent):
        """Response should match source documents"""
        response = agent.chat(
            "What is the income tax exemption?",
            "test_accuracy"
        )
        
        if response["retrieved"]:
            assert "800" in response["response"] or "exempt" in response["response"].lower()
    
    def test_response_time(self, agent):
        """Response should be generated within acceptable time"""
        start = time.time()
        
        response = agent.chat(
            "Will I pay more tax?",
            "test_time"
        )
        
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Response took {elapsed:.2f} seconds"


class TestErrorHandling:
    """Test error scenarios"""
    
    def test_empty_message(self, agent):
        """Should handle empty messages gracefully"""
        response = agent.chat("", "test_empty")
        assert len(response["response"]) > 0
    
    def test_very_long_message(self, agent):
        """Should handle very long messages"""
        long_message = "What about tax? " * 100
        response = agent.chat(long_message, "test_long")
        assert len(response["response"]) > 0


class TestSessionManagement:
    """Test session handling"""
    
    def test_different_sessions_isolated(self, agent):
        """Different sessions should have separate histories"""
        session1 = "user_1"
        session2 = "user_2"
        
        agent.chat("Hello", session1)
        agent.chat("Will I pay more tax?", session2)
        
        history1 = agent.get_conversation_history(session1)
        history2 = agent.get_conversation_history(session2)
        
        assert len(history1) != len(history2)
    
    def test_session_clearing(self, agent):
        """Should be able to clear session history"""
        session_id = "test_clear"
        
        agent.chat("Hello", session_id)
        agent.chat("What about tax?", session_id)
        
        agent.clear_session(session_id)
        
        history = agent.get_conversation_history(session_id)
        assert len(history) == 0


TEST_QUERIES = {
    "greetings": [
        "Hello",
        "Hi there",
        "Good morning"
    ],
    "simple_policy": [
        "Will I pay more income tax?",
        "How does VAT work now?",
        "What happens to small businesses?"
    ],
    "specific_questions": [
        "What is the income tax exemption threshold?",
        "How is VAT distributed across states?",
        "When does the new tax law start?"
    ],
    "follow_ups": [
        "Tell me more",
        "What about Lagos?",
        "Can you explain that better?"
    ],
    "edge_cases": [
        "",
        "aksdjfhaksjdfh",
        "Tax? Tax! TAX!!!",
        "What if I earn N1,000,000?"
    ]
}


def run_manual_tests(agent: TaxQAAgent):
    """Run manual tests with sample queries"""
    print("\n" + "="*60)
    print("MANUAL TEST SUITE")
    print("="*60 + "\n")
    
    for category, queries in TEST_QUERIES.items():
        print(f"\nTesting: {category.upper()}")
        print("-" * 60)
        
        for query in queries:
            print(f"\nQuery: {query}")
            
            try:
                response = agent.chat(query, f"manual_test_{category}")
                
                print(f"Response: {response['response'][:150]}...")
                print(f"Retrieved: {response['retrieved']}")
                print(f"Sources: {len(response.get('sources', []))}")
                
            except Exception as e:
                print(f"Error: {e}")


def benchmark_agent(agent: TaxQAAgent, num_queries: int = 10):
    """Benchmark agent performance"""
    import statistics
    
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60 + "\n")
    
    queries = [
        "Will I pay more tax?",
        "How does VAT work?",
        "What about small businesses?",
    ] * (num_queries // 3)
    
    times = []
    
    for i, query in enumerate(queries, 1):
        start = time.time()
        response = agent.chat(query, f"benchmark_{i}")
        elapsed = time.time() - start
        times.append(elapsed)
    
    print(f"Queries processed: {len(times)}")
    print(f"Average time: {statistics.mean(times):.2f}s")
    print(f"Fastest: {min(times):.2f}s")
    print(f"Slowest: {max(times):.2f}s")
    print(f"Median: {statistics.median(times):.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    
    print("\n\nRunning manual tests...")
    from document_processor import load_and_chunk_documents
    
    chunks = load_and_chunk_documents()
    if chunks:
        store = VectorStore()
        store.create_collection(reset=True)
        store.add_documents(chunks)
        
        test_agent = create_agent(store)
        
        run_manual_tests(test_agent)
        benchmark_agent(test_agent)
    else:
        print("No documents to test with!")