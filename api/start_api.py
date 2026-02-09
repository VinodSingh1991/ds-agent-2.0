"""
Start the Disposable UI Agent API server

Usage:
    python start_api.py
    python start_api.py --port 8080
    python start_api.py --host 0.0.0.0 --port 8000 --reload
"""

import argparse
import uvicorn
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Start Disposable UI Agent API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", default="info", help="Log level (default: info)")
    
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 Starting Disposable UI Agent API")
    print("="*80)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {args.reload}")
    print(f"Log Level: {args.log_level}")
    print("="*80)
    print(f"\n📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health Check: http://{args.host}:{args.port}/health")
    print(f"🎯 Generate Endpoint: http://{args.host}:{args.port}/generate")
    print("\nPress CTRL+C to stop the server\n")
    print("="*80 + "\n")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Start server
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()

