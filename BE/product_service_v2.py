# product_service_v2.py
from neo4j_client import get_driver
from typing import List, Optional, Dict, Any
from neo4j import GraphDatabase
from models import ProductCreate, ProductUpdate, SearchFilters
import time

class ProductServiceV2:
    def __init__(self):
        self.driver = get_driver()

    def close(self):
        self.driver.close()

    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Create a new product in Neo4j"""
        try:
            with self.driver.session() as session:
                # Get next product ID
                next_id = self._get_next_product_id(session)
                
                product_dict = product_data.dict()
                product_dict["id"] = next_id
                product_dict["created_at"] = time.time()
                product_dict["updated_at"] = time.time()

                session.run(
                    """
                    CREATE (p:Product {
                        id: $id,
                        name: $name,
                        category: $category,
                        brand: $brand,
                        price: $price,
                        description: $description,
                        tags: $tags,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    """,
                    **product_dict
                )
                return {"success": True, "product_id": next_id, "data": product_dict}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_featured_products(self, limit: int = 6):
        query = """
        MATCH (p:Product)
        WHERE p.featured = true
        RETURN p { .* } AS product
        ORDER BY p.rating DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            results = session.run(query, limit=limit)
            return [record["product"] for record in results]

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (p:Product {id: $id}) RETURN p", {"id": product_id}
                )
                record = result.single()
                if record:
                    return dict(record["p"])
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_all_products(self) -> List[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (p:Product) RETURN p ORDER BY p.id ASC")
                return [dict(record["p"]) for record in result]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def _get_next_product_id(self, session) -> int:
        result = session.run("MATCH (p:Product) RETURN coalesce(max(p.id), 0) AS max_id")
        max_id = result.single()["max_id"]
        return max_id + 1

product_service_v2 = ProductServiceV2()
