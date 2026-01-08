"""
agent.py
LangGraph agent with conditional retrieval and conversation memory
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from google import genai

from .config import config, SYSTEM_PROMPTS
from .vector_store import VectorStore
from .memory import ConversationMemory


# =============================================================================
# STATE DEFINITION
# =============================================================================

class AgentState(TypedDict):
    """State passed through LangGraph nodes"""
    session_id: str
    user_message: str
    conversation_history: List[Dict]
    retrieved_documents: Optional[List[Dict]]
    should_retrieve: bool
    generated_response: Optional[str]
    sources: Optional[List[Dict]]
    timestamp: datetime


# =============================================================================
# TAX Q&A AGENT
# =============================================================================

class TaxQAAgent:
    """
    Agentic RAG system for Nigeria Tax Reform Bills
    
    Flow:
    1. Receive user message
    2. Decide if retrieval needed
    3. Retrieve documents (if needed)
    4. Generate response with citations
    5. Update conversation memory
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.memory = ConversationMemory()
        
        # Initialize Gemini client
        self.llm = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.LLM_MODEL
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("decide_retrieval", self.decide_retrieval)
        workflow.add_node("retrieve_documents", self.retrieve_documents)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define edges
        workflow.set_entry_point("decide_retrieval")
        
        # Conditional routing based on should_retrieve
        workflow.add_conditional_edges(
            "decide_retrieval",
            self.route_after_decision,
            {
                "retrieve": "retrieve_documents",
                "generate": "generate_response"
            }
        )
        
        workflow.add_edge("retrieve_documents", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    # =========================================================================
    # NODE 1: DECIDE IF RETRIEVAL IS NEEDED
    # =========================================================================
    
    def decide_retrieval(self, state: AgentState) -> AgentState:
        """
        Decide if we need to retrieve documents
        
        Logic:
        - Greetings/thanks → NO retrieval
        - Policy questions → YES retrieval
        - Follow-ups → Check if context sufficient
        """
        user_message = state["user_message"].lower().strip()
        conversation_history = state["conversation_history"]
        
        # Simple rule-based for greetings
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        thanks = ["thank", "thanks", "appreciate"]
        
        if any(g in user_message for g in greetings) or any(t in user_message for t in thanks):
            state["should_retrieve"] = False
            return state
        
        # Use LLM for more complex decisions
        decision_prompt = f"""
{SYSTEM_PROMPTS['retrieval_decision']}

User Message: "{state['user_message']}"

Recent Conversation:
{self._format_history(conversation_history[-3:] if conversation_history else [])}

Decision (RETRIEVE or NO_RETRIEVE):"""
        
        try:
            response = self.llm.models.generate_content(
                model=self.model,
                contents=decision_prompt,
                config={
                    "temperature": 0.0,
                    "max_output_tokens": 50
                }
            )
            
            decision = response.text.strip().upper()
            state["should_retrieve"] = "RETRIEVE" in decision
            
        except Exception as e:
            print(f"⚠️ Decision error: {e}. Defaulting to RETRIEVE")
            state["should_retrieve"] = True
        
        return state
    
    def route_after_decision(self, state: AgentState) -> str:
        """Route based on retrieval decision"""
        return "retrieve" if state["should_retrieve"] else "generate"
    
    # =========================================================================
    # NODE 2: RETRIEVE DOCUMENTS
    # =========================================================================
    
    def retrieve_documents(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from vector store"""
        query = state["user_message"]
        
        print(f"🔍 Retrieving documents for: '{query}'")
        
        # Search vector store
        documents = self.vector_store.similarity_search(
            query=query,
            k=config.RETRIEVAL_TOP_K
        )
        
        if documents:
            print(f"📄 Retrieved {len(documents)} documents")
            state["retrieved_documents"] = documents
        else:
            print("⚠️ No relevant documents found")
            state["retrieved_documents"] = []
        
        return state
    
    # =========================================================================
    # NODE 3: GENERATE RESPONSE
    # =========================================================================
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM"""
        
        # Build context
        context = self._build_context(state)
        
        # Generate response
        try:
            response = self.llm.models.generate_content(
                model=self.model,
                contents=context,
                config={
                    "temperature": config.TEMPERATURE,
                    "max_output_tokens": config.MAX_TOKENS,
                    "top_p": config.TOP_P
                }
            )
            
            generated_text = response.text
            
            # Extract citations
            # FIX: Ensure we treat None as empty list to avoid iteration errors
            docs = state.get("retrieved_documents") or []
            sources = self._extract_sources(docs)
            
            state["generated_response"] = generated_text
            state["sources"] = sources
            
            print("✅ Response generated successfully")
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            state["generated_response"] = "Sorry, I encountered an error generating a response."
            state["sources"] = []
        
        return state
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _build_context(self, state: AgentState) -> str:
        """Build context for LLM"""
        parts = [SYSTEM_PROMPTS["main"]]
        
        # Add conversation history
        if state.get("conversation_history"):
            parts.append("\nConversation History:")
            parts.append(self._format_history(state["conversation_history"]))
        
        # Add retrieved documents
        if state.get("retrieved_documents"):
            parts.append("\nRelevant Information from Documents:")
            for i, doc in enumerate(state["retrieved_documents"], 1):
                parts.append(f"\n[Document {i}]")
                parts.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
                parts.append(f"Content: {doc['content'][:1500]}...") # Increased context window for accuracy
                parts.append(f"Relevance Score: {doc['score']:.2f}")
        
        # Add current question
        parts.append(f"\nCurrent Question: {state['user_message']}")
        parts.append("\nYour Response (with citations):")
        
        return "\n".join(parts)
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history"""
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.title()}: {content}")
        return "\n".join(formatted)
    
    def _extract_sources(self, documents: List[Dict]) -> List[Dict]:
        """Extract citation information from documents"""
        sources = []
        
        # FIX: Safety check for None documents
        if not documents:
            return []
        
        for doc in documents:
            source_info = {
                "document": doc["metadata"].get("source", "Unknown"),
                "type": doc["metadata"].get("type", "Unknown"),
                "score": doc["score"],
                "excerpt": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            }
            sources.append(source_info)
        
        return sources
    
    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    
    def chat(
        self,
        message: str,
        session_id: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Main chat interface
        
        Args:
            message: User's question
            session_id: Session identifier
            conversation_history: Previous messages
        
        Returns:
            Response dict with answer and sources
        """
        # Initialize state
        initial_state = AgentState(
            session_id=session_id,
            user_message=message,
            conversation_history=conversation_history or [],
            retrieved_documents=[],  # FIX: Initialize as empty list instead of None
            should_retrieve=False,
            generated_response=None,
            sources=[],  # FIX: Initialize as empty list instead of None
            timestamp=datetime.now()
        )
        
        # Run through graph
        print(f"\n🤖 Processing: '{message}'")
        final_state = self.graph.invoke(initial_state)
        
        # Update memory
        self.memory.add_message(
            session_id=session_id,
            role="user",
            content=message
        )
        
        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=final_state["generated_response"]
        )
        
        # Return response
        return {
            "session_id": session_id,
            "response": final_state["generated_response"],
            "sources": final_state.get("sources", []),
            "retrieved": final_state["should_retrieve"],
            "timestamp": final_state["timestamp"].isoformat()
        }
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.memory.get_history(session_id)
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        self.memory.clear_session(session_id)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_agent(vector_store: VectorStore) -> TaxQAAgent:
    """Create and return initialized agent"""
    agent = TaxQAAgent(vector_store)
    print("✅ Tax Q&A Agent initialized")
    return agent