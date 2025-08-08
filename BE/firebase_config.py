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
                # First try: Look for serviceAccountKey.json in the same directory
                service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                
                if os.path.exists(service_account_path):
                    # Use service account file
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized with serviceAccountKey.json")
                else:
                    # Try to get service account path from environment
                    env_service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                    
                    if env_service_account_path and os.path.exists(env_service_account_path):
                        # Use service account file from environment
                        cred = credentials.Certificate(env_service_account_path)
                        firebase_admin.initialize_app(cred)
                        print("✅ Firebase initialized with service account file from environment")
                    else:
                        print(f"❌ Service account key not found at: {service_account_path}")
                        print("Please make sure 'serviceAccountKey.json' is in the BE folder")
                        raise FileNotFoundError("Firebase service account key not found")
            
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
