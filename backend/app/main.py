# # backend/app/main.py

# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from app.api import chat
# from app.services import ai_engine
# from contextlib import asynccontextmanager
# import asyncio
# import logging

# # -----------------------
# # Logging Configuration
# # -----------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger(__name__)

# # -----------------------
# # Lifespan: Async startup/shutdown
# # -----------------------
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     FastAPI lifespan context manager:
#     - Initializes AI engine in background
#     - Server responds to /health immediately
#     """
#     logger.info("🚀 Starting AI Engine in background...")
#     asyncio.create_task(ai_engine.initialize_ai_engine())
#     yield
#     logger.info("🛑 Application shutdown complete")

# # -----------------------
# # FastAPI App Initialization
# # -----------------------
# app = FastAPI(
#     title="Nigeria Tax Q&A Assistant",
#     lifespan=lifespan
# )

# # -----------------------
# # CORS Middleware (FIX for Issue #8)
# # -----------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -----------------------
# # Global Error Handling Middleware
# # -----------------------
# @app.middleware("http")
# async def global_exception_middleware(request: Request, call_next):
#     """
#     Catches all exceptions, logs them, and returns a safe 500 response.
#     """
#     try:
#         return await call_next(request)
#     except Exception as exc:
#         logger.exception(f"Unhandled exception: {exc}")
#         return JSONResponse(
#             status_code=500,
#             content={"detail": "Internal server error. Please try again later."}
#         )

# # -----------------------
# # Include API Routers
# # -----------------------
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# # -----------------------
# # Health Check Endpoint
# # -----------------------
# @app.get("/health")
# async def health():
#     """
#     Health check endpoint.
#     Returns immediately even if AI engine is still initializing.
#     """
#     return {
#         "status": "ready",
#         "ai_agent_initialized": ai_engine._initialized
#     }

# # -----------------------
# # Root Endpoint
# # -----------------------
# @app.get("/")
# async def root():
#     return {"message": "Welcome to Nigeria Tax Q&A Assistant API"}









# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.services import ai_engine
from contextlib import asynccontextmanager
import asyncio
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# -----------------------
# Logging Configuration
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------
# Rate Limiter
# -----------------------
limiter = Limiter(key_func=get_remote_address)

# -----------------------
# Lifespan
# -----------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Engine in background...")
    asyncio.create_task(ai_engine.initialize_ai_engine())
    yield
    logger.info("🛑 Application shutdown complete")

# -----------------------
# FastAPI Init
# -----------------------
app = FastAPI(
    title="Nigeria Tax Q&A Assistant",
    lifespan=lifespan
)

# Attach limiter to app state
app.state.limiter = limiter

# -----------------------
# Rate Limit Exception Handler
# -----------------------
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."}
    )

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Global Error Middleware
# -----------------------
@app.middleware("http")
async def global_exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# -----------------------
# Routers
# -----------------------
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# -----------------------
# Health
# -----------------------
@app.get("/health")
async def health():
    return {
        "status": "ready",
        "ai_agent_initialized": ai_engine._initialized
    }