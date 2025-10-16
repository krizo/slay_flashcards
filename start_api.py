#!/usr/bin/env python3
"""
SlayFlashcards API startup script
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import uvicorn  # pylint: disable=import-error

from api.api_config import settings, is_development

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def kill_process_on_port(port: int):
    """Kill any process using the specified port."""
    try:
        # Find process using the port
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    pid_int = int(pid)
                    print(f"🔄 Killing existing process on port {port} (PID: {pid_int})")
                    os.kill(pid_int, signal.SIGKILL)
                except (ValueError, ProcessLookupError, OSError) as e:
                    print(f"⚠️  Could not kill process {pid}: {e}")

            # Give the OS time to release the port
            time.sleep(1)
            print(f"✅ Port {port} is now available")
    except FileNotFoundError:
        # lsof not available, try alternative method
        try:
            # Alternative for systems without lsof
            subprocess.run(
                ["pkill", "-9", "-f", "uvicorn"],
                check=False,
                capture_output=True
            )
            time.sleep(1)
        except FileNotFoundError:
            pass


def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description="SlayFlashcards API Server")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=settings.workers, help="Number of worker processes")
    parser.add_argument("--log-level", default=settings.log_level.lower(), help="Log level")
    parser.add_argument("--env", default=settings.environment, help="Environment (development/production)")
    parser.add_argument("--force", action="store_true", help="Force kill any existing process on the port")

    args = parser.parse_args()

    # Kill existing process if --force or in development mode
    if args.force or is_development() or args.reload:
        kill_process_on_port(args.port)

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
