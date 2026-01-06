# backend/app/middleware/error_handler.py

import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """
    Catches all unhandled exceptions across the FastAPI app.
    Prevents internal errors from leaking to the client.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log full exception server-side
            print(f"[ERROR] Unhandled exception: {exc}")
            traceback.print_exc()

            # Return generic error to client
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error."}
            )
