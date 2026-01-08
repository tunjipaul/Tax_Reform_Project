


# backend/app/main.py




from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import chat
from app.services import ai_engine
from contextlib import asynccontextmanager
import asyncio
import logging

# -----------------------
# Logging Configuration
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------
# Lifespan: Async startup/shutdown
# -----------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager:
    - Initializes AI engine in background
    - Server responds to /health immediately
    """
    logger.info("🚀 Starting AI Engine in background...")
    asyncio.create_task(ai_engine.initialize_ai_engine())
    yield
    logger.info("🛑 Application shutdown complete")

# -----------------------
# FastAPI App Initialization
# -----------------------
app = FastAPI(
    title="Nigeria Tax Q&A Assistant",
    lifespan=lifespan
)

# -----------------------
# Global Error Handling Middleware
# -----------------------
@app.middleware("http")
async def global_exception_middleware(request: Request, call_next):
    """
    Catches all exceptions, logs them, and returns a safe 500 response.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Log full internal error
        logger.exception(f"Unhandled exception: {exc}")
        # Return sanitized error to client
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."}
        )

# -----------------------
# Include API Routers
# -----------------------
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# -----------------------
# Health Check Endpoint
# -----------------------
@app.get("/health")
async def health():
    """
    Health check endpoint.
    Returns immediately even if AI engine is still initializing.
    """
    return {
        "status": "ready",
        "ai_agent_initialized": ai_engine.initialized
    }

# -----------------------
# Root Endpoint
# -----------------------
@app.get("/")
async def root():
    return {"message": "Welcome to Nigeria Tax Q&A Assistant API"}
