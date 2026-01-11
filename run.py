#!/usr/bin/env python3
"""
Entry point for running the ANPR backend server.
"""
import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Add project root to Python path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "src.backend.main:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes for development
        log_level="info"
    )
