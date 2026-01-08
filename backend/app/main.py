"""
=============================================================================
SMARTCAREER AI - MAIN APPLICATION
=============================================================================

FastAPI application entry point.

FEATURES:
    - API versioning (v1)
    - CORS configuration
    - Health checks
    - Exception handlers
    - Startup/shutdown events

RUN WITH:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

DOCS:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import ssl

# Local imports
from app.config import settings, print_config_summary
from app.api.v1 import api_router
from app.database import check_database_connection

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure structured logging for production
if settings.DEBUG:
    # Development logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
else:
    # Production structured logging
    import json
    import sys
    from datetime import datetime

    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            # Add extra fields if they exist
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'endpoint'):
                log_entry['endpoint'] = record.endpoint

            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.formatException(record.exc_info)

            return json.dumps(log_entry)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler for production
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party logs in production
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# =============================================================================
# LIFESPAN EVENTS
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    
    Startup:
        - Log configuration
        - Check database connection
        - Initialize services
    
    Shutdown:
        - Close connections
        - Cleanup resources
    """
    # =========================================================================
    # STARTUP
    # =========================================================================
    
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Print configuration summary
    if settings.DEBUG:
        print_config_summary()
    
    # Check database connection
    if check_database_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed!")
    
    # Log API info
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # =========================================================================
    # SHUTDOWN
    # =========================================================================
    
    logger.info("=" * 60)
    logger.info(f"👋 Shutting down {settings.APP_NAME}...")
    logger.info("=" * 60)


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    
    application = FastAPI(
        title=settings.APP_NAME,
        description="""
        ## SmartCareer AI API
        
        AI-powered career platform API for resume generation and job matching.
        
        ### Features
        - 👤 **Authentication**: Register, login, JWT tokens
        - 📄 **Resumes**: Create, edit, AI-generate resumes
        - 💼 **Jobs**: Browse, search, post job listings
        - 📨 **Applications**: Apply to jobs, track status
        
        ### Authentication
        Most endpoints require a Bearer token in the Authorization header:
        ```
        Authorization: Bearer <your_access_token>
        ```
        
        Get a token by calling `POST /api/v1/auth/login`.
        """,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # =========================================================================
    # CORS MIDDLEWARE
    # =========================================================================
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =========================================================================
    # HTTPS REDIRECT MIDDLEWARE (PRODUCTION)
    # =========================================================================

    if settings.FORCE_HTTPS and not settings.DEBUG:
        application.add_middleware(HTTPSRedirectMiddleware)
    
    # =========================================================================
    # INCLUDE ROUTERS
    # =========================================================================
    
    # API v1
    application.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    return application


# =============================================================================
# CREATE APP INSTANCE
# =============================================================================

app = create_application()


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Returns user-friendly error messages.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip "body"
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle database errors.
    
    Logs the actual error but returns generic message to user.
    """
    logger.exception(f"Database error: {exc}")
    
    # Log to error service
    try:
        from app.services.error_logging_service import error_logger, ErrorCategory, ErrorSeverity
        await error_logger.log_database_error(
            error=exc,
            operation="query",
            extra_data={
                "endpoint": request.url.path,
                "method": request.method,
            }
        )
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected errors.
    
    Logs the error and returns a generic message.
    """
    logger.exception(f"Unexpected error: {exc}")
    
    # Log to error service
    try:
        from app.services.error_logging_service import error_logger, ErrorCategory, ErrorSeverity
        await error_logger.log_api_error(
            error=exc,
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            ip_address=request.client.host if request.client else None,
        )
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    response_model=Dict[str, Any]
)
async def root():
    """
    Root endpoint - returns API info.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_model=Dict[str, Any]
)
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.
    
    Returns:
        - status: "healthy" or "unhealthy"
        - database: connection status
        - version: app version
        - timestamp: current UTC timestamp
        - environment: current environment
    """
    import time
    from app.database import get_db_info

    db_healthy = check_database_connection()
    db_info = get_db_info() if db_healthy else {}
    
    health_status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
    }

    # Add database info if available and healthy
    if db_healthy and db_info:
        health_status["database_info"] = {
            "pool_size": db_info.get("pool_size"),
            "checked_out": db_info.get("checked_out"),
            "overflow": db_info.get("overflow"),
        }

    return health_status


@app.get(
    "/health/detailed",
    tags=["Health"],
    summary="Detailed health check",
    response_model=Dict[str, Any]
)
async def detailed_health_check():
    """
    Detailed health check with comprehensive system information.

    Returns detailed health metrics for monitoring systems.
    """
    import time
    import psutil
    from app.database import get_db_info

    start_time = time.time()
    db_healthy = check_database_connection()
    db_check_time = time.time() - start_time

    # Get system metrics
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent,
        }
    }

    health_status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "response_time_ms": round(db_check_time * 1000, 2),
                "info": get_db_info() if db_healthy else {},
            }
        },
        "system": system_info,
        "version": settings.APP_VERSION,
        "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
        "uptime": time.time() - psutil.boot_time(),
    }

    return health_status


@app.get(
    "/api",
    tags=["Health"],
    summary="API info",
    response_model=Dict[str, Any]
)
async def api_info():
    """
    API information endpoint.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "resumes": "/api/v1/resumes",
            "jobs": "/api/v1/jobs",
            "applications": "/api/v1/applications",
        }
    }


# =============================================================================
# HTTPS REDIRECT ENDPOINT (for load balancers)
# =============================================================================

@app.get("/.well-known/health-check")
async def health_check_well_known():
    """
    Well-known health check endpoint for load balancers and monitoring.
    """
    return await health_check()


# =============================================================================
# SSL CONTEXT HELPER
# =============================================================================

def create_ssl_context():
    """
    Create SSL context for HTTPS server.

    Returns SSL context if SSL is enabled and certs are available.
    """
    if not settings.SSL_ENABLED or not settings.SSL_CERTFILE or not settings.SSL_KEYFILE:
        return None

    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=settings.SSL_CERTFILE,
            keyfile=settings.SSL_KEYFILE
        )
        logger.info(f"✅ SSL context created with cert: {settings.SSL_CERTFILE}")
        return ssl_context
    except Exception as e:
        logger.error(f"❌ Failed to create SSL context: {e}")
        return None


# =============================================================================
# RUN DIRECTLY (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    # SSL configuration
    ssl_context = create_ssl_context()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.HTTPS_PORT if ssl_context else 8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        ssl_certfile=settings.SSL_CERTFILE if ssl_context else None,
        ssl_keyfile=settings.SSL_KEYFILE if ssl_context else None,
    )
