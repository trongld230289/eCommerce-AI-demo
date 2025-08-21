import os
import sys
from typing import List, Dict, Any
import httpx

# Add parent directory to path to import services
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


class MiddlewareService:
    def __init__(self):
        pass

    def simple_semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simple semantic search that takes a query string and returns a list of products.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of product dictionaries
        """
        try:
            # Get embedding for the query
            query_embedding = self.ai_service.get_embedding(query)
            if not query_embedding:
                return []
            
            # Set up search parameters
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": limit,
                "include": ["metadatas", "documents", "distances"]
            }
            
            # Query the collection
            results = self.ai_service.collection.query(**search_params)
            
            products = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    # Calculate similarity score
                    distance = results["distances"][0][i]
                    similarity_score = 1 - (distance / 2)  # Normalize to [0, 1] range
                    
                    # Only include products with reasonable similarity
                    if similarity_score > 0.1:
                        product_data = {
                            "id": metadata["id"],
                            "name": metadata["name"],
                            "category": metadata["category"],
                            "price": metadata["price"],
                            "original_price": metadata["original_price"],
                            "rating": metadata["rating"],
                            "discount": metadata["discount"],
                            "imageUrl": metadata["imageUrl"],
                            "similarity_score": similarity_score
                        }
                        products.append(product_data)
            
            return products
            
        except Exception as e:
            print(f"Error in simple semantic search: {str(e)}")
            return []
    
    def find_gifts_external(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find gifts external function that fetches gift recommendations from the gifting endpoint.
        
        Args:
            query: The search query for gifting.
            limit: The maximum number of results per label (default: 10).
        
        Returns:
            List of gift recommendation dictionaries with labels and product IDs
        """
        # Thuong implementation - gift endpoint

        url = "http://localhost:8003/gift"  # Assuming the main backend runs on port 8003
        payload = {
            "query": query,
            "limit": limit
        }
        
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch gifts: {response.text}")
            
            recommendations = response.json()
            return recommendations

    def get_recommendations_external(self, product_ids: List[int], user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find gifts external function that fetches gift recommendations from the recommendation endpoint.
        
        Args:
            product_ids: List of product IDs to base recommendations on.
            user_id: Optional user ID for personalized recommendations.
        
        Returns:
            List of gift recommendation dictionaries with labels and product IDs
        """
        # Thuong implementation - get recommendation endpoint
        
        url = "http://localhost:8003/get-recommendations"
        payload = {
            "product_ids": product_ids,
            "user_id": user_id
        }
        
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch recommendations: {response.text}")
            
            recommendations = response.json()
            return recommendations
    
    def push_user_after_registration(self, user_id: str, user_email: str, user_name: str) -> Dict[str, str]:
        """
        Process user registration data after successful account creation.
        
        Args:
            user_id: Firebase user ID
            user_email: User email address
            user_name: User display name
            
        Returns:
            Dictionary with status and message
        """
        try:
            # Log the inputs as requested
            print("=== push_user_after_registration ===")
            print(f"userId: {user_id}")
            print(f"userEmail: {user_email}")
            print(f"userName: {user_name}")
            print("====================================")

            # Thuong implementation push user info
        
            data = {
                "userId": user_id,
                "name": user_name,
                "email": user_email
            }
            
            url = "http://localhost:8003/register-user"
            response = httpx.post(url, json=data)
            
            if response.status_code != 200:
                raise Exception(f"Failed to register user: HTTP {response.status_code}")
            
            # Here you can add additional logic such as:
            # - Save user to database
            # - Send welcome email
            # - Create user profile
            # - Initialize user preferences
            # - etc.
            
            return {
                "status": "success",
                "message": f"User {user_name} registered successfully"
            }
            
        except Exception as e:
            print(f"Error in push_user_after_registration: {str(e)}")
            return {
                "status": "error",
                "message": f"User registration processing failed: {str(e)}"
            }

# Create a global instance for easy access
middleware_service = MiddlewareService()

def simple_semantic_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function for simple semantic search.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of product dictionaries
    """
    return middleware_service.simple_semantic_search(query, limit)

def find_gifts_external() -> List[Dict[str, Any]]:
    """
    Convenience function for finding gifts external.
    
    Returns:
        List of gift recommendation dictionaries with labels and product IDs
    """
    return middleware_service.find_gifts_external()

def get_recommendations_external() -> List[Dict[str, Any]]:
    """
    Convenience function for getting recommendations external.
    
    Returns:
        List of gift recommendation dictionaries with labels and product IDs
    """
    return middleware_service.get_recommendations_external()

def push_user_after_registration(user_id: str, user_email: str, user_name: str) -> Dict[str, str]:
    """
    Convenience function for processing user registration.
    
    Args:
        user_id: Firebase user ID
        user_email: User email address
        user_name: User display name
        
    Returns:
        Dictionary with status and message
    """
    return middleware_service.push_user_after_registration(user_id, user_email, user_name)
