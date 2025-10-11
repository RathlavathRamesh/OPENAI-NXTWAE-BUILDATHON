#!/usr/bin/env python3
"""
Start the Disaster Response Server
"""

import os
import sys
import uvicorn
from config import GEMINI_API_KEY, HOST, PORT, DEBUG

def main():
    print("🚀 Starting Disaster Response System")
    print("=" * 50)
    
    # Set the API key from config file
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("❌ Please update your API key in config.py")
        print("   Edit config.py and replace 'YOUR_GEMINI_API_KEY_HERE' with your actual key")
        return
    
    print(f"✅ Using Gemini API key: {GEMINI_API_KEY[:10]}...")
    print(f"🌐 Server starting on http://{HOST}:{PORT}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🎯 Main Endpoint: POST http://localhost:8000/take_request")
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "app:app",
            host=HOST,
            port=PORT,
            reload=DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")

if __name__ == "__main__":
    main()
