"""
BolKhata Server Launcher
Run with: python run.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting BolKhata Server on http://{settings.host}:{settings.port} ...")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
