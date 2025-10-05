#!/usr/bin/env python3
"""
SlayFlashcards API startup script
"""
import argparse
import sys
from pathlib import Path

import uvicorn  # pylint: disable=import-error

from api.api_config import settings, is_development

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description="SlayFlashcards API Server")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=settings.workers, help="Number of worker processes")
    parser.add_argument("--log-level", default=settings.log_level.lower(), help="Log level")
    parser.add_argument("--env", default=settings.environment, help="Environment (development/production)")

    args = parser.parse_args()

    # Update settings based on arguments
    settings.environment = args.env

    print("🚀 Starting SlayFlashcards API Server")
    print(f"📍 Environment: {settings.environment}")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print(f"📚 Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 Database: {settings.database_url}")

    # Development vs Production settings
    if is_development() or args.reload:
        print("🔄 Development mode: Auto-reload enabled")
        uvicorn.run(
            "api.main_api:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level=args.log_level,
            access_log=True
        )
    else:
        print(f"⚡ Production mode: {args.workers} workers")
        uvicorn.run(
            "api.main_api:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level=args.log_level,
            access_log=True,
            loop="uvloop",  # Performance optimization
            http="httptools"  # Performance optimization
        )


if __name__ == "__main__":
    main()
