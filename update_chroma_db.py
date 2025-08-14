#!/usr/bin/env python3
"""
ChromaDB Update Script
This script clears the existing ChromaDB collection and re-embeds all products
with updated keywords for better semantic search performance.
"""

import requests
import json

def update_chroma_db():
    """Clear ChromaDB and re-embed all products"""
    print('🔄 Starting ChromaDB clear and re-embedding process...')
    
    try:
        response = requests.post('http://localhost:8000/api/ai/embed-products')
        print('Status Code:', response.status_code)
        
        if response.status_code == 200:
            result = response.json()
            print('✅ Response:', json.dumps(result, indent=2))
            return True
        else:
            print('❌ Error:', response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print('❌ Error: Could not connect to backend server on localhost:8000')
        print('Please make sure the backend server is running.')
        return False
    except Exception as e:
        print(f'❌ Unexpected error: {str(e)}')
        return False

if __name__ == "__main__":
    success = update_chroma_db()
    if success:
        print('\n🎉 ChromaDB update completed successfully!')
        print('You can now test searches like "laptop under 1200" to see MacBooks included.')
    else:
        print('\n💡 To start the backend server, run:')
        print('cd BE && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload')
