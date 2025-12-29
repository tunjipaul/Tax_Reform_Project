

---

## 🏗️ WHAT IS SYSTEM ARCHITECTURE?

**System Architecture = A diagram showing:**
- All the components/pieces of your system
- How they connect to each other
- How data flows between them
- Who talks to who and when

**Like a blueprint of a house showing:**
- Kitchen connects to living room
- Electrical outlets and wiring
- Water pipes location
- How everything works together

---

## 📊 YOUR TAX Q&A ASSISTANT ARCHITECTURE



```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  ┌────────────────────────────────────────────────┐    │
│  │  Chat Interface (User sees this)               │    │
│  │  - Message input box                           │    │
│  │  - Message display area                        │    │
│  │  - Source citations display                    │    │
│  │  - Loading indicator                           │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         │ (sends: message + session_id) │
│                         │ (receives: answer + sources)  │
│                         ▼                                │
└─────────────────────────────────────────────────────────┘
                         │
                         │ HTTP Request/Response
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                     │
│  ┌────────────────────────────────────────────────┐    │
│  │  API Endpoints                                 │    │
│  │  POST /api/chat                                │    │
│  │  - Receives: {message, session_id}             │    │
│  │  - Returns: {response, sources, session_id}    │    │
│  │                                                │    │
│  │  Session Management                            │    │
│  │  - Create session_id                           │    │
│  │  - Store conversation history                  │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         │ (passes: context + question)  │
│                         │ (receives: answer)            │
│                         ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  AI Engine (LangGraph Agent)                   │    │
│  │  - Decides: Should I retrieve documents?       │    │
│  │  - If yes: Retrieves from vector DB            │    │
│  │  - Uses conversation memory for context        │    │
│  │  - Generates answer with citations             │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         │ (retrieves: document chunks)  │
│                         ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Vector Database (Chroma)                      │    │
│  │  - Stores: Tax bill text as embeddings         │    │
│  │  - Does semantic search                        │    │
│  │  - Returns: Relevant document sections         │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 HOW DATA FLOWS (Step by Step)

### **User Types a Question:**

```
1. USER (React Frontend)
   ├─ Types: "Will I pay more tax?"
   ├─ Clicks Send
   └─ Sends to Backend:
      {
        "session_id": "abc123xyz",
        "message": "Will I pay more tax?"
      }

2. BACKEND (FastAPI)
   ├─ Receives message
   ├─ Checks: Is this session_id known?
   │  └─ If NO: Create new session
   ├─ Retrieves conversation history for this session
   └─ Passes to AI Engine:
      {
        "current_question": "Will I pay more tax?",
        "session_id": "abc123xyz",
        "conversation_history": []  (empty, first message)
      }

3. AI ENGINE (LangGraph)
   ├─ Analyzes: "This is asking about tax policy"
   ├─ Decides: "YES, I need to retrieve documents"
   ├─ Asks Vector DB: 
   │  "Find sections about income tax changes"
   └─ Vector DB returns:
      [
        "Nigeria Tax Bill 2024, Section 12: Income tax rates...",
        "Nigeria Tax Bill 2024, Section 15: Income thresholds..."
      ]

4. AI GENERATES ANSWER
   ├─ Uses retrieved documents as context
   ├─ Generates: "Yes, income tax has changed. Based on..."
   ├─ Cites: "[Source: Nigeria Tax Bill 2024, Section 12]"
   └─ Stores in conversation memory:
      {
        "session_id": "abc123xyz",
        "messages": [
          {"role": "user", "content": "Will I pay more tax?"},
          {"role": "assistant", "content": "Yes, income tax..."}
        ]
      }

5. RESPONSE BACK TO USER
   ├─ Backend receives answer from AI
   ├─ Sends to Frontend:
      {
        "session_id": "abc123xyz",
        "response": "Yes, income tax...",
        "sources": [
          {
            "document": "Nigeria Tax Bill 2024",
            "section": "Section 12",
            "text": "Income tax rates are..."
          }
        ]
      }

6. FRONTEND DISPLAYS
   ├─ Shows assistant response
   ├─ Shows source citations
   ├─ Ready for next question
   └─ SAVES session_id for next message
```

---

## 🧩 THE 3 MAIN COMPONENTS

### **1. FRONTEND (React)**
```
What it does:
- User types question
- Shows assistant response
- Shows conversation history (in this session)
- Shows source citations
- Sends HTTP requests to backend

What it contains:
- Chat message component
- Input box component
- Source citation component
- Loading state component
- Error message component

Technologies:
- React
- Tailwind CSS
- Fetch (for HTTP requests)
```

### **2. BACKEND (FastAPI)**
```
What it does:
- Receives HTTP requests from frontend
- Manages sessions and conversation history
- Connects frontend to AI engine
- Returns formatted responses

What it contains:
- POST /api/chat endpoint
- Session management logic
- Conversation storage (in-memory)
- Error handling

Technologies:
- FastAPI
- Python
- Pydantic (for data validation)
```

### **3. AI ENGINE (LangGraph + Chroma)**
```
What it does:
- Decides if documents need to be retrieved
- Retrieves relevant documents from vector DB
- Generates answers with citations
- Maintains conversation context

What it contains:
- LangGraph agent logic
- Document retrieval logic
- Vector database connection
- Citation extraction

Technologies:
- LangChain & LangGraph
- Chroma (vector database)
- OpenAI embeddings
```

---



## 🎨 SIMPLE ARCHITECTURE

**Copy this and modify for your kickoff:**

```
┌─────────────────────────────────────┐
│     USER / BROWSER                  │
└────────────────────┬────────────────┘
                     │
          HTTP POST /api/chat
    {session_id, message, ...}
                     │
                     ▼
┌─────────────────────────────────────┐
│       REACT FRONTEND                │
│  - Chat input & display             │
│  - Session ID management            │
│  - Show sources                     │
└────────────────┬────────────────────┘
                 │
      HTTP Request/Response (JSON)
                 │
                 ▼
┌─────────────────────────────────────┐
│      FASTAPI BACKEND                │
│  - /api/chat endpoint               │
│  - Session management               │
│  - Conversation storage             │
│  - Error handling                   │
└────────────────┬────────────────────┘
                 │
     Python function call
    (question, context, history)
                 │
                 ▼
┌─────────────────────────────────────┐
│    LANGGRAPH AI AGENT               │
│  - Conditional retrieval logic      │
│  - Context awareness                │
│  - Citation generation              │
└────────────────┬────────────────────┘
                 │
    Semantic search query
    "Find info about income tax"
                 │
                 ▼
┌─────────────────────────────────────┐
│     CHROMA VECTOR DATABASE          │
│  - Nigeria Tax Bill chunks          │
│  - Embeddings/Semantic search       │
│  - Returns relevant sections        │
└─────────────────────────────────────┘
```

---

## 💾 DATA FLOW DETAILS

### **What Gets Passed Between Components:**

**Frontend → Backend:**
```json
{
  "session_id": "user_abc_123",
  "message": "Will I pay more tax?"
}
```

**Backend → AI Engine:**
```python
{
  "question": "Will I pay more tax?",
  "session_history": [
    "Previous Q: ...",
    "Previous A: ..."
  ]
}
```

**AI Engine → Vector DB:**
```
Query: "income tax changes new law"
(This is a semantic search query)
```

**Vector DB → AI Engine:**
```
Results: [
  {
    "document": "Nigeria Tax Bill 2024, Section 12",
    "text": "Income tax rates are...",
    "similarity_score": 0.95
  },
  {
    "document": "Nigeria Tax Bill 2024, Section 15",
    "text": "Income thresholds are...",
    "similarity_score": 0.87
  }
]
```

**AI Engine → Backend:**
```json
{
  "response": "Yes, income tax has changed to...",
  "sources": [
    {
      "document": "Nigeria Tax Bill 2024",
      "section": "Section 12",
      "text": "Income tax rates..."
    }
  ]
}
```

**Backend → Frontend:**
```json
{
  "session_id": "user_abc_123",
  "response": "Yes, income tax...",
  "sources": [
    {
      "document": "Nigeria Tax Bill 2024",
      "section": "Section 12"
    }
  ]
}
```

---

## ✅  ARCHITECTURE DOCUMENT 



1. **High-level diagram** 
   - Shows 4 components
   - Shows how they connect
   - Shows data flow

2. **Component descriptions**
   - What does frontend do?
   - What does backend do?
   - What does AI do?
   - What does database do?

3. **Technology stack**
   - Frontend: React + Tailwind + Fetch
   - Backend: FastAPI + Python
   - AI: LangChain + LangGraph
   - Database: Chroma(AI Engineer's initiative)

4. **Data formats**
   - What JSON is sent?
   - What data types?
   - Request/response examples

5. **Sequence flow**
   - Step 1: User types message
   - Step 2: Frontend sends to backend
   - Step 3: Backend calls AI
   - Step 4: AI retrieves documents
   - Step 5: AI generates answer
   - Step 6: Response goes back to user

---







## 💡 TECHNICAL EXAMPLE: What Happens When Chidi Asks a Question

**Chidi on frontend:**
```
Types: "Will I earn more as a software developer?"
Clicks: Send
```

**What happens behind scenes:**

```
1. React Frontend
   - Collects: {session_id: "chidi_xyz", message: "Will I earn..."}
   - Sends: POST request to http://backend.com/api/chat

2. FastAPI Backend
   - Receives POST request
   - Validates data
   - Looks up session_id in conversation store
   - Retrieves previous messages (empty, first time)
   - Calls AI Engine with:
     {
       "question": "Will I earn more as a software developer?",
       "context": []
     }

3. LangGraph AI Agent
   - Analyzes: "This is a tax question about income"
   - Decides: "Yes, I need to retrieve documents"
   - Sends to Chroma: Query "software developer income tax personal income"

4. Chroma Vector Database
   - Searches embeddings
   - Finds: 
     * Section on personal income tax rates
     * Section on software/tech worker incentives
   - Returns: Top 3 relevant sections

5. LangGraph continues
   - Receives document sections
   - Generates answer: "As a software developer, your income is subject to..."
   - Adds citations: "[Source: Nigeria Tax Bill 2024, Section 45]"
   - Stores in memory: 
     {
       "session_id": "chidi_xyz",
       "messages": [
         "Q: Will I earn more...",
         "A: As a software developer..."
       ]
     }

6. FastAPI Backend
   - Receives answer from AI
   - Formats response:
     {
       "session_id": "chidi_xyz",
       "response": "As a software developer...",
       "sources": [{
         "document": "Nigeria Tax Bill 2024",
         "section": "45",
         "excerpt": "..."
       }]
     }
   - Sends back to Frontend

7. React Frontend
   - Receives response
   - Displays: Assistant message + sources
   - Saves session_id for next message
   - Chidi sees answer!

Chidi asks follow-up: "What about VAT on my services?"
- Frontend sends: {session_id: "chidi_xyz", message: "What about VAT..."}
- Backend retrieves conversation from session_id
- AI sees: "This is about VAT and software developer"
- AI remembers: "We were discussing software developer taxes"
- AI gives contextual answer!
```

---

