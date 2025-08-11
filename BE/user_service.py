# user_service_v2.py
from typing import List, Optional, Dict, Any
from neo4j_client import get_driver
import time
import uuid
import bcrypt

class UserServiceV2:
    def __init__(self):
        self.driver = get_driver()

    def close(self):
        self.driver.close()

    # ==============================
    # REGISTER
    # ==============================
    def register(self, email: str, password: str, displayName: str,
                 description: str = "", preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Register a new user with hashed password"""
        try:
            # Check if email already exists
            with self.driver.session() as session:
                existing = session.run(
                    "MATCH (u:User {email: $email}) RETURN u", {"email": email}
                ).single()
                if existing:
                    return {"success": False, "error": "Email already registered"}

                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                user_dict = {
                    "userId": str(uuid.uuid4()),
                    "email": email,
                    "password": hashed_pw,
                    "displayName": displayName,
                    "description": description,
                    "categories": preferences.get("categories", []) if preferences else [],
                    "brands": preferences.get("brands", []) if preferences else [],
                    "created_at": time.time(),
                    "updated_at": time.time()
                }

                session.run(
                    """
                    CREATE (u:User {
                        userId: $userId,
                        email: $email,
                        password: $password,
                        displayName: $displayName,
                        description: $description,
                        preferences: {categories: $categories, brands: $brands},
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    """,
                    **user_dict
                )
                return {"success": True, "userId": user_dict["userId"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==============================
    # LOGIN
    # ==============================
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user by verifying email and password"""
        try:
            with self.driver.session() as session:
                record = session.run(
                    "MATCH (u:User {email: $email}) RETURN u", {"email": email}
                ).single()
                if not record:
                    return {"success": False, "error": "User not found"}

                user = dict(record["u"])
                if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                    return {"success": False, "error": "Invalid password"}

                return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==============================
    # ADD / UPDATE PROFILE
    # ==============================
    def add_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add or update user profile details.
        Example profile_data:
        {
            "displayName": "John Doe",
            "description": "A passionate shopper",
            "preferences": {
                "categories": ["Electronics", "Books"],
                "brands": ["Apple", "Sony"]
            }
        }
        """
        try:
            profile_data["updated_at"] = time.time()
            # Flatten preferences
            categories = profile_data.get("preferences", {}).get("categories", [])
            brands = profile_data.get("preferences", {}).get("brands", [])

            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (u:User {userId: $userId})
                    SET u.displayName = $displayName,
                        u.description = $description,
                        u.preferences = {categories: $categories, brands: $brands},
                        u.updated_at = $updated_at
                    """,
                    userId=user_id,
                    displayName=profile_data.get("displayName", ""),
                    description=profile_data.get("description", ""),
                    categories=categories,
                    brands=brands,
                    updated_at=profile_data["updated_at"]
                )
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==============================
    # CRUD
    # ==============================
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (u:User {userId: $userId}) RETURN u", {"userId": user_id}
                )
                record = result.single()
                if record:
                    return dict(record["u"])
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (u:User) RETURN u ORDER BY u.created_at DESC")
                return [dict(record["u"]) for record in result]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        try:
            with self.driver.session() as session:
                session.run("MATCH (u:User {userId: $userId}) DETACH DELETE u", {"userId": user_id})
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_to_wishlist(self, product_name: str, product_category: str, product_brand: str,
                        product_price: float, user_id: str) -> dict:
        """
        Adds a product to a user's wishlist in Neo4j.
        Creates product node if not existing and relationship WISHLISTED.
        """
        try:
            with self.driver.session() as session:
                # First check if user exists
                user_exists = session.run(
                    "MATCH (u:User {userId: $userId}) RETURN u",
                    {"userId": user_id}
                ).single()

                if not user_exists:
                    return {"success": False, "error": "User not found"}

                # Create or match product, then link
                session.run(
                    """
                    MERGE (p:Product {name: $name, category: $category, brand: $brand})
                    ON CREATE SET p.price = $price, 
                                  p.created_at = $now,
                                  p.updated_at = $now
                    ON MATCH SET p.updated_at = $now
                    WITH p
                    MATCH (u:User {userId: $userId})
                    MERGE (u)-[r:WISHLISTED]->(p)
                    ON CREATE SET r.created_at = $now
                    """,
                    {
                        "name": product_name,
                        "category": product_category,
                        "brand": product_brand,
                        "price": product_price,
                        "userId": user_id,
                        "now": time.time()
                    }
                )

                return {"success": True, "message": f"Product '{product_name}' added to wishlist"}
        except Exception as e:
            return {"success": False, "error": str(e)}

user_service_v2 = UserServiceV2()
