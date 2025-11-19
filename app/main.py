from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
import re
from dotenv import load_dotenv

from .services.database import get_db
from .routes import router
from .schemas import ErrorDetail

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Note: Database tables are created/updated via Alembic migrations
# Run 'alembic upgrade head' to apply migrations

app = FastAPI(
    title="Room Reservation System",
    description="RESTful API for room reservation management with conflict validation and soft delete",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with wildcard support
def is_origin_allowed(origin: str, allowed_origins: list) -> bool:
    """
    Check if an origin is allowed, supporting wildcard patterns.
    Supports patterns like *.ismaelnascimento.com
    """
    if not origin:
        return False
    
    # Check exact matches first
    if origin in allowed_origins:
        return True
    
    # Check wildcard patterns
    for allowed_origin in allowed_origins:
        if '*' in allowed_origin:
            # Convert wildcard pattern to regex
            # *.ismaelnascimento.com -> .*\.ismaelnascimento\.com
            pattern = allowed_origin.replace('.', r'\.').replace('*', '.*')
            if re.match(f'^{pattern}$', origin):
                return True
    
    return False

def cors_middleware_handler(origin: str) -> bool:
    """Custom CORS origin handler that supports wildcards"""
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,https://*.ismaelnascimento.com,http://*.ismaelnascimento.com")
    allowed_origins = [origin.strip() for origin in cors_origins_str.split(",")]
    return is_origin_allowed(origin, allowed_origins)

# Custom CORS handler using middleware (supports wildcard patterns)
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    """Custom CORS handler that supports wildcard patterns"""
    origin = request.headers.get("origin")
    
    if request.method == "OPTIONS":
        # Handle preflight requests
        if origin:
            if cors_middleware_handler(origin):
                response = JSONResponse(content={}, status_code=200)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Max-Age"] = "3600"
                return response
            else:
                # Reject preflight if origin not allowed
                return JSONResponse(content={"error": "CORS not allowed"}, status_code=403)
        # If no origin header, proceed normally (same-origin request)
    
    response = await call_next(request)
    
    # Add CORS headers if origin is allowed
    if origin and cors_middleware_handler(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Include routes
app.include_router(router, prefix="/api")


# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorDetail(
            message="Erro de validação nos dados fornecidos",
            code="VALIDATION_ERROR",
            details={"errors": errors}
        ).model_dump()
    )


# Global exception handler for SQLAlchemy errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemy errors."""
    error_message = str(exc)
    logger.error(f"Database error: {error_message}", exc_info=True)
    
    # Determine if it's a connection error
    is_connection_error = any(keyword in error_message.lower() for keyword in [
        "connection", "connect", "could not connect", "timeout", 
        "network", "refused", "unreachable", "no such host"
    ])
    
    # In development, include more details
    is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    details = None
    if is_dev:
        details = {
            "error_type": type(exc).__name__,
            "error_message": error_message
        }
    
    message = "Internal server error processing request"
    if is_connection_error:
        message = "Error connecting to database. Please verify the database is running and accessible."
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetail(
            message=message,
            code="DATABASE_ERROR",
            details=details
        ).model_dump()
    )


# Global exception handler for generic exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler for unhandled exceptions."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetail(
            message="Internal server error",
            code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    )


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Room Reservation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """
    API health check.
    Verifies database connectivity.
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
