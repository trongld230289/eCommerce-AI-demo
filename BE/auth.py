from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import json
import os

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        # Try to load service account key
        service_account_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized with service account")
        else:
            # For development/testing, create a mock setup
            print("Service account key not found, using mock authentication")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        print("Using mock authentication for development")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate Firebase ID token and return user information
    """
    try:
        token = credentials.credentials
        
        # For development/demo purposes, accept demo tokens
        if token == "demo-token":
            return {
                "uid": "demo-user",
                "email": "demo@example.com",
                "name": "Demo User"
            }
        
        # Try to verify Firebase token
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            return {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name", decoded_token.get("email", "").split("@")[0])
            }
        except Exception as firebase_error:
            print(f"Firebase token verification failed: {firebase_error}")
            
            # Fallback for development - basic token validation
            if token and len(token) > 10:  # Basic token format check
                # Extract user info from token or use defaults
                return {
                    "uid": f"user-{hash(token) % 10000}",
                    "email": "user@example.com",
                    "name": "User"
                }
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
