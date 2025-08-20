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
<<<<<<< HEAD
        
        # For development/demo purposes, accept demo tokens
        if token == "demo-token":
=======
        print(f"AUTH DEBUG: Received token: {token[:20]}...")
        
        # For development/demo purposes, accept demo tokens
        if token == "demo-token":
            print("AUTH DEBUG: Using demo token")
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            return {
                "uid": "demo-user",
                "email": "demo@example.com",
                "name": "Demo User"
            }
        
        # Try to verify Firebase token
        try:
            decoded_token = firebase_auth.verify_id_token(token)
<<<<<<< HEAD
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
=======
            user_uid = decoded_token.get("uid")
            
            # Get comprehensive user info from Firebase Auth
            try:
                user_record = firebase_auth.get_user(user_uid)
                user_info = {
                    "uid": user_uid,
                    "email": user_record.email or decoded_token.get("email"),
                    "name": user_record.display_name or decoded_token.get("name") or (user_record.email.split("@")[0] if user_record.email else "User")
                }
                print(f"Firebase auth successful from user record:")
                print(f"  uid: {user_info['uid']}")
                print(f"  email: {user_info['email']}")
                print(f"  name: {user_info['name']}")
                print(f"  user_record.email: {user_record.email}")
                print(f"  user_record.display_name: {user_record.display_name}")
                
            except Exception as record_error:
                print(f"Could not get user record, using token data: {record_error}")
                user_info = {
                    "uid": user_uid,
                    "email": decoded_token.get("email"),
                    "name": decoded_token.get("name", decoded_token.get("email", "").split("@")[0] if decoded_token.get("email") else "User")
                }
                print(f"Firebase auth from token only:")
                print(f"  uid: {user_info['uid']}")
                print(f"  email: {user_info['email']}")
                print(f"  name: {user_info['name']}")
            
            print(f"Decoded token keys: {list(decoded_token.keys())}")
            return user_info
        except Exception as firebase_error:
            print(f"AUTH DEBUG: Firebase token verification failed: {firebase_error}")
            print(f"AUTH DEBUG: Token: {token[:20]}...")
            
            # Fallback for development - use a consistent user ID based on token
            if token and len(token) > 10:
                # Use a consistent hash for the same token
                import hashlib
                consistent_uid = f"user-{hashlib.md5(token.encode()).hexdigest()[:10]}"
                
                # Try to get real user info from Firebase Auth using the known UID pattern
                try:
                    # If we can map this to a real Firebase UID, try to get user info
                    real_uid = "bWn5vC8uHrXeFGkSg6L50nevm1n1"  # Your actual Firebase UID
                    user_record = firebase_auth.get_user(real_uid)
                    user_info = {
                        "uid": real_uid,
                        "email": user_record.email,
                        "name": user_record.display_name or (user_record.email.split("@")[0] if user_record.email else "User")
                    }
                    print(f"AUTH DEBUG: Using fallback with real user data: uid={user_info['uid']}, email={user_info['email']}, name={user_info['name']}")
                except Exception as user_error:
                    print(f"AUTH DEBUG: Could not get real user data: {user_error}")
                    user_info = {
                        "uid": consistent_uid,
                        "email": None,
                        "name": None
                    }
                    print(f"AUTH DEBUG: Using fallback with null data: uid={user_info['uid']}")
                
                return user_info
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            
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
