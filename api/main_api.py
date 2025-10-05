"""
FastAPI application for SlayFlashcards API
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status  # pylint: disable=import-error
from fastapi.middleware.cors import CORSMiddleware  # pylint: disable=import-error
from fastapi.responses import JSONResponse  # pylint: disable=import-error

from api.dependencies import auth
from api.middleware.error_handler import ErrorHandlerMiddleware
from api.middleware.request_logging import RequestLoggingMiddleware
from api.routes import flashcards_route, quizzes_route, sessions_route, users_route
from core.db.database import Base, SessionLocal, engine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=redefined-outer-name,unused-argument
    """Application lifespan manager."""
    # Startup
    logger.info("Starting SlayFlashcards API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down SlayFlashcards API...")


# Create FastAPI application
app = FastAPI(
    title="SlayFlashcards API",
    description="REST API for SlayFlashcards - An interactive flashcard learning platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Dependency to get database session
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SlayFlashcards API", "version": "1.0.0"}


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users_route.router, prefix="/api/v1/users", tags=["users"])
app.include_router(quizzes_route.router, prefix="/api/v1/quizzes", tags=["quizzes"])
app.include_router(flashcards_route.router, prefix="/api/v1/flashcards", tags=["flashcards"])
app.include_router(sessions_route.router, prefix="/api/v1/sessions", tags=["sessions"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


if __name__ == "__main__":
    import uvicorn  # pylint: disable=import-error

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
