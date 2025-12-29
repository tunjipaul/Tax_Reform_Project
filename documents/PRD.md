# PRODUCT REQUIREMENTS DOCUMENT
## Nigeria Tax Reform Bills 2024 Q&A Assistant

**Version:** 1.0  
**Date:** December 2025  
**Product Manager:** Me

---

## EXECUTIVE SUMMARY

We're building an AI-powered Q&A assistant that helps Nigerians understand the 2024 tax reform bills. The bills are complex (500+ pages of legal language), and most people don't know how they'll be affected. Our solution makes this information accessible and trustworthy.

When someone asks "Will I pay more tax?", they should get an accurate, source-backed answer in under 3 seconds.

---

## THE PROBLEM

Small businesses with annual turnover of ₦50 million or less are exempt from income tax, workers earning ₦800,000 annually are fully exempted, and essential items like food, education, and healthcare have 0% VAT. But most Nigerians don't know this.

Instead, they hear:
- "I'll pay 50% tax now" (panic)
- "This destroys the North" (politics)
- "Small businesses will collapse" (misinformation)

The actual bills address these concerns. But nobody reads 500 pages of legal documents.

Real people asking right now:
- "Will I pay more income tax?"
- "How does VAT derivation affect my state?"
- "What's the difference between old and new tax rules?"
- "When does this start?"
- "How will this affect my business?"
- "Which states benefit most?"

---

## OUR SOLUTION

A chat interface where users ask tax questions and get:
1. Accurate answers from the actual bills
2. Direct citations (so it's not just an opinion)
3. Contextual responses (follow-ups build on previous questions)
4. Smart retrieval (doesn't fetch documents for "Hello!")
5. Everything in clear, plain Nigerian English

---

## WHO WE'RE SOLVING FOR

**Aunty Ngozi** - Small restaurant owner in Lagos. Heard about taxes on radio, terrified. Needs to know: Will she pay more? How much? When?

**Chidi** - Software developer. Wants specifics. Will his income tax go up or down? What's his new bracket?

**Governor Yahaya** - State governor. Needs to understand VAT distribution. Which states benefit? What's the calculation?

**Any Nigerian** needing facts backed by official documents.

---

## CORE FEATURES

### 1. Answer Tax Questions with Document Retrieval

User asks something tax-related. System searches the actual bills, finds relevant sections, provides an answer. No guessing, no opinions.

**Acceptance Criteria:**
- Answers 90%+ of test questions correctly
- Factually accurate (verified against source documents)
- Relevant information (not generic)
- Response time < 3 seconds
- No hallucinations

**Test Cases:**
- "Will I pay more income tax?" → Cite specific sections about income tax changes
- "How does VAT derivation work?" → Explain new VAT formula with sources
- "What happens to small businesses?" → Point to business-related sections
- "When does this start?" → Give specific date with citation

---

### 2. Cite Sources

Every answer includes where it came from. Format: "Nigeria Tax Bill 2024, Section 45". Users can click to see actual text.

**Acceptance Criteria:**
- Every answer has at least one source
- Sources are clickable/expandable
- No answer without a source
- Sources are accurate

---

### 3. Conversation Memory

```
Q1: "Will I pay more tax?"
A1: [Answers about tax changes]

Q2: "What if I earn ₦500k/year?"
A2: [Remembers Q1, gives income-specific answer]

Q3: "How does VAT fit in?"
A3: [Knows about both taxes, answers holistically]
```

Without this, the assistant would ask "What about your previous question?" every time.

**Acceptance Criteria:**
- System remembers previous questions
- Follow-ups use previous context
- Doesn't repeat information already given
- History persists during session
- Includes at least 5 previous messages

---

### 4. Smart Retrieval (Agentic Behavior)

- User: "Hello!" → Assistant responds without fetching documents
- User: "What's VAT?" → Fetches documents first
- User: "Tell me more" → Uses memory, not new retrieval

Don't waste time retrieving for every message. Think first.

**Acceptance Criteria:**
- Greetings don't trigger retrieval
- Policy questions do trigger retrieval
- Follow-ups use memory
- Decision-making is logged
- Response time for non-retrieval < 1 second

---

### 5. Chat Interface

Simple, clean, professional. Message input, response display, source citations visible. Works on mobile.

**Acceptance Criteria:**
- Input box and send button work
- Messages appear chronologically
- Assistant messages look different from user messages
- Mobile responsive
- Scrolls properly with many messages
- Professional design

---

### 6. Loading & Error States

Show "Thinking..." while processing. Show clear error messages if something breaks.

**Acceptance Criteria:**
- Loading indicator visible
- Error messages are helpful
- System recovers gracefully
- User always knows what's happening

---

## SYSTEM ARCHITECTURE

```
User Types Question
        ↓
   REACT FRONTEND
   (Chat Interface)
        ↓
   HTTP POST /api/chat
   {session_id, message}
        ↓
   FASTAPI BACKEND
   (API + Session Management)
        ↓
   LANGGRAPH AI ENGINE
   (Decision Logic + Context)
        ↓
   CHROMA VECTOR DB
   (Document Search)
        ↓
   Response Returns to User
```

**Technology Stack:**
- Frontend: React + Tailwind CSS + Fetch
- Backend: FastAPI + Python
- AI: LangChain + LangGraph
- Database: Chroma (vector database)
- Embeddings: OpenAI or Hugging Face or Gemini API
- Session Storage: In-memory dictionary

---

## DATA FLOW EXAMPLE

Chidi asks: "Will my income tax increase?"

1. Frontend sends: `{session_id: "chidi_123", message: "Will my income tax increase?"}`
2. Backend receives, checks session, passes to AI
3. AI decides: "This needs document retrieval"
4. Chroma searches for income tax sections
5. AI receives: Nigeria Tax Bill 2024, Sections 12-15
6. AI generates: "Yes, income tax rates have changed. Based on the new law..."
7. Includes citation: [Source: Nigeria Tax Bill 2024, Section 13]
8. Stores in memory: `sessions["chidi_123"]` now includes this Q&A

Chidi's follow-up: "What if I earn ₦500k?"
- Same session_id used
- Backend retrieves conversation history
- AI knows it's about income tax
- Provides personalized answer without re-fetching

---

## DOCUMENTS WE'RE USING

Primary:
- Nigeria Tax Bill 2024
- Nigeria Tax Administration Bill 2024
- Nigeria Revenue Service Act 2024
- Joint Revenue Board Act 2024

Supporting (for comparison):
- Finance Act 2023
- Presidential statements on reform
- Official FAQs and clarifications

---

## TIMELINE

| What | Duration | When |
|-----|----------|------|
| Planning & Requirements | Days 1-3 | Dec 23-25 |
| Core Development | Days 4-9 | Dec 26-31 |
| Integration & Testing | Days 10-12 | Jan 1-3 |
| Polish & Demo | Days 13-14 | Jan 4-6 |
| Submission | Day 15 | Jan 7, 10 AM |

---

## SUCCESS LOOKS LIKE

✓ Answers 90%+ of test questions correctly  
✓ Every answer has proper citations  
✓ Conversation memory works perfectly  
✓ Smart retrieval works (no unnecessary fetching)  
✓ Response time < 3 seconds  
✓ No hallucinations  
✓ Professional UI  
✓ Mobile responsive  
✓ Error handling is graceful  
✓ Full documentation provided  
✓ Demo video shows all features

---

## WHAT WE'RE NOT BUILDING

- User authentication/login
- Multi-language support
- Mobile app (web only)
- Voice input/output
- Analytics dashboard
- Email notifications
- Conversation export to PDF
- Admin dashboard

These would add a week of work. Not worth it for this capstone.

---

## ASSUMPTIONS

- Users have internet
- Users can type in English
- Documents are text format (not scanned images)
- We have access to an LLM API
- Chroma works reliably
- We have 2 weeks and 4 people

---

## TEAM RESPONSIBILITIES

**AI Engineer:** Build the LangGraph agent, document retrieval logic, conversation memory, citation extraction

**Backend Engineer:** FastAPI endpoints, session management, conversation storage, error handling

**Frontend Engineer:** React chat UI, responsive design, source display, loading states

**Project Manager:** Make sure everyone understands this, block obstacles, test as we build, deliver on time

---

## NEXT STEPS

1. Everyone reads this document
2. Ask any questions
3. Agree we're building exactly this
4. Start building