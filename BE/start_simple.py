"""
Simple start script for the FastAPI backend server without migration
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting eCommerce Backend API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
