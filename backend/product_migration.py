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
                    print("[SUCCESS] Firebase initialized with serviceAccountKey.json")
                else:
                    # Try to get service account path from environment
                    env_service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                    
                    if env_service_account_path and os.path.exists(env_service_account_path):
                        # Use service account file from environment
                        cred = credentials.Certificate(env_service_account_path)
                        firebase_admin.initialize_app(cred)
                        print("[SUCCESS] Firebase initialized with service account file from environment")
                    else:
                        print(f"[ERROR] Service account key not found at: {service_account_path}")
                        print("Please make sure 'serviceAccountKey.json' is in the BE folder")
                        raise FileNotFoundError("Firebase service account key not found")
            
            # Get Firestore client
            self.db = firestore.client()
            print("[SUCCESS] Firebase Firestore client initialized")
            
        except Exception as e:
            print(f"[ERROR] Firebase initialization failed: {e}")
            print("   Running in development mode without database")
            # Set db to None so we can handle it gracefully
            self.db = None
    
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

def migrate_from_firestore_to_json():
    db = get_firestore_db()
    if db is None:
        print("Database not initialized. Exiting.")
        return

    collection_ref = db.collection('products')  # Assuming the collection name is 'products'

    docs = collection_ref.stream()

    transformed_products = []

    for doc in docs:
        data = doc.to_dict()
        
        # Map common fields
        new_product = {
            "productId": data.get('id'),
            "name": data.get('name'),
            "price": data.get('price'),
            "original_price": data.get('original_price'),
            "image": data.get('imageUrl'),
            "description": data.get('description'),
            "created_at": int(data.get('created_at', 0) * 1000) if data.get('created_at') else 0,
            "updated_at": int(data.get('updated_at', 0) * 1000) if data.get('updated_at') else 0,
        }
        
        # Generate additional fields based on category (and optionally description)
        category = data.get('category', '')
        
        # gifting_categories = []
        # tags = []
        # utilitarian_score = 0.5
        # novelty_score = 0.5
        # relationship_types = []
        # symbolic_value = "low"
        # altruism_suitability = "medium"
        # reciprocity_fit = "low"
        # self_gifting_suitability = "medium"
        # target_genders = ["unisex"]
        
        # if category == "Phone":
        #     gifting_categories = ["birthday", "graduation", "holidays"]
        #     tags = ["smartphone", "mobile", "tech"]
        #     utilitarian_score = 0.95
        #     novelty_score = 0.7
        #     relationship_types = ["family", "friends", "romantic"]
        #     symbolic_value = "medium"
        #     altruism_suitability = "high"
        #     reciprocity_fit = "high"
        #     self_gifting_suitability = "high"
        #     if "gaming" in description:
        #         gifting_categories.append("gaming")
        #         tags.append("gaming")
        
        # # You can add more category-based logic here for other potential categories
        
        new_product.update({
            "tags": [category]
        })
        
        transformed_products.append(new_product)

    # Save to local JSON file
    with open('transformed_products.json', 'w') as json_file:
        json.dump(transformed_products, json_file, indent=4)
    
    print("Products have been fetched from Firestore, transformed, and saved to 'transformed_products.json'.")

if __name__ == "__main__":
    migrate_from_firestore_to_json()