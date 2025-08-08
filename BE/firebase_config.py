import os
import json
from typing import Optional
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

class FirebaseConfig:
    def __init__(self):
        self.db = None
        self.init_firebase()
    
    def init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Try to get service account path from environment
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                
                if service_account_path and os.path.exists(service_account_path):
                    # Use service account file
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized with service account file")
                else:
                    # Use Firebase project configuration (for same project as frontend)
                    firebase_config = {
                        "type": "service_account",
                        "project_id": "ecommerce-ai-cfafd",
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                    }
                    
                    # Check if we have the required environment variables
                    if firebase_config["private_key"] and firebase_config["client_email"]:
                        cred = credentials.Certificate(firebase_config)
                        firebase_admin.initialize_app(cred)
                        print("✅ Firebase initialized with environment variables")
                    else:
                        # For development: Use a mock configuration
                        print("⚠️  No Firebase credentials found. Using mock configuration for development.")
                        print("   To connect to real Firebase, add credentials to .env file")
                        # Initialize with minimal config for development
                        cred = credentials.ApplicationDefault()
                        firebase_admin.initialize_app(cred, {
                            'projectId': 'ecommerce-ai-cfafd'
                        })
            
            # Get Firestore client
            self.db = firestore.client()
            print("✅ Firebase Firestore client initialized")
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            print("   Running in development mode without database")
            # Set db to None so we can handle it gracefully
            self.db = None
    
    def get_db(self):
        """Get Firestore database instance"""
        return self.db
    
    def get_db(self):
        """Get Firestore database instance"""
        if self.db is None:
            self.init_firebase()
        return self.db

# Global Firebase instance
firebase_config = FirebaseConfig()

def get_firestore_db():
    """Get Firestore database instance"""
    return firebase_config.get_db()
