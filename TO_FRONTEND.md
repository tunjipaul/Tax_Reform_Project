```
FRONTEND_INTEGRATION_GUIDE.md
```

and it will work immediately.

---

```md
# Frontend Integration Guide

**To:** Frontend Team  
**From:** Samuel (AI Engineer)

The AI Backend is ready
This document explains how to connect your **React frontend** to the **Q&A Engine**.

---

## API Base URL

### Local Development
```

[http://localhost:8000](http://localhost:8000)

````

---

## 1. Chat Endpoint

### POST `/api/chat`

Use this endpoint to send user messages and receive AI-generated answers **with citations**.

---

### Request Body

```json
{
  "session_id": "user_123_session",
  "message": "Will I pay more income tax?",
  "history": []
}
````

#### Field Descriptions

- **session_id**

  - Generate a UUID when the frontend loads
  - Used to maintain conversation context

- **message**

  - The user's current question

- **history** (optional)

  - Array of previous messages if you want to manage history client-side

---

### Response Body

```json
{
  "session_id": "user_123_session",
  "response": "Based on the Nigeria Tax Act 2025, personal income tax is...",
  "sources": [
    {
      "document": "Nigeria Tax Act 2025.pdf",
      "type": "pdf",
      "score": 0.61,
      "excerpt": "...tax due for any accounting period shall be payable..."
    }
  ],
  "retrieved": true,
  "timestamp": "2026-01-08T14:30:00"
}
```

#### Response Fields

- **response**

  - The AI-generated answer

- **sources**

  - List of documents used to generate the response
  - Empty array if no relevant sources were found

- **retrieved**

  - `true` if document retrieval was used

- **timestamp**

  - ISO 8601 formatted response time

---

## 2. Health Check

### GET `/health`

Use this endpoint for your **System Status** indicator.

---

### Response

```json
{
  "status": "healthy",
  "ai_engine": "connected"
}
```

---

## UI Recommendations

### Citations

- When `sources` is **not empty**, display them below the AI response
- Suggested UI patterns:

  - Small source cards
  - Or a **“View Sources”** dropdown

---

### Loading State

- AI response time: **2–4 seconds**
- Recommended loading message:

  > _"Searching tax documents..."_

---

### Disclaimer

Always show this footer message in the UI:

> **AI can make mistakes. Please check official documents.**

---

## Running the Backend (Local Testing)

1. Navigate to the project root
2. Run the command:

```bash
python -m backend.main
```

3. The API will be available at:

```
http://localhost:8000
```

---

## Notes for Frontend Integration

- Handle empty `sources` gracefully
- Persist `session_id` for the duration of a user session
- Expect non-instant responses (do not block UI)
- Treat AI responses as **assistive**, not authoritative

---
