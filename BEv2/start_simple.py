"""
Simple start script for the FastAPI backend server v2 (Neo4j Edition)
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from environment variable or default to 8010
    port = int(os.getenv("PORT", 8010))
    
    print("🚀 Starting eCommerce Backend API Server v2 (Neo4j Edition)...")
    print(f"📍 Server will be available at: http://localhost:{port}")
    print("📊 Database: Neo4j")
    print(f"📖 API documentation at: http://localhost:{port}/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        reload=True,
        log_level="info"
    )
