from typing import List, Optional, Dict, Any
from database_config import get_neo4j_driver
from models import Product, ProductCreate, ProductUpdate, SearchFilters
import time
from datetime import datetime

class Neo4jProductService:
    def __init__(self):
        self.driver = get_neo4j_driver()
        
        if self.driver is None:
            raise Exception("Neo4j connection failed. Please check your configuration.")
    
    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Create a new product in Neo4j"""
        try:
            with self.driver.session() as session:
                # Get next available ID
                next_id = self._get_next_product_id(session)
                
                # Convert to dict and add ID and timestamps
                product_dict = product_data.dict()
                product_dict['id'] = next_id
                product_dict['created_at'] = datetime.now().isoformat()
                product_dict['updated_at'] = datetime.now().isoformat()
                
                # Create product node in Neo4j
                create_query = """
                CREATE (p:Product {
                    id: $id,
                    name: $name,
                    brand: $brand,
                    category: $category,
                    price: $price,
                    description: $description,
                    stock: $stock,
                    rating: $rating,
                    reviews: $reviews,
                    featured: $featured,
                    image_url: $image_url,
                    created_at: $created_at,
                    updated_at: $updated_at,
                    weeklySales: $weeklySales,
                    weeklyViews: $weeklyViews
                })
                
                // Create/connect brand
                MERGE (b:Brand {name: $brand})
                MERGE (p)-[:MANUFACTURED_BY]->(b)
                
                // Create/connect category
                MERGE (c:Category {name: $category})
                MERGE (p)-[:BELONGS_TO]->(c)
                
                RETURN p
                """
                
                params = {
                    'id': product_dict['id'],
                    'name': product_dict.get('name', ''),
                    'brand': product_dict.get('brand', ''),
                    'category': product_dict.get('category', ''),
                    'price': float(product_dict.get('price', 0)),
                    'description': product_dict.get('description', ''),
                    'stock': int(product_dict.get('stock', 0)),
                    'rating': float(product_dict.get('rating', 0)),
                    'reviews': int(product_dict.get('reviews', 0)),
                    'featured': bool(product_dict.get('featured', False)),
                    'image_url': product_dict.get('image_url', ''),
                    'created_at': product_dict['created_at'],
                    'updated_at': product_dict['updated_at'],
                    'weeklySales': int(product_dict.get('weeklySales', 0)),
                    'weeklyViews': int(product_dict.get('weeklyViews', 0))
                }
                
                result = session.run(create_query, params)
                result.single()
                
                return {"success": True, "product_id": next_id, "data": product_dict}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID from Neo4j"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (p:Product {id: $product_id})
                RETURN p
                """
                
                result = session.run(query, {'product_id': product_id})
                record = result.single()
                
                if record:
                    return dict(record['p'])
                return None
        except Exception as e:
            print(f"Error getting product {product_id}: {e}")
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from Neo4j"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (p:Product)
                RETURN p
                ORDER BY p.id
                """
                
                result = session.run(query)
                products = []
                
                for record in result:
                    product_data = dict(record['p'])
                    products.append(product_data)
                
                return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Dict[str, Any]:
        """Update product in Neo4j"""
        try:
            with self.driver.session() as session:
                # Check if product exists
                check_query = "MATCH (p:Product {id: $product_id}) RETURN count(p) as count"
                check_result = session.run(check_query, {'product_id': product_id})
                exists = check_result.single()['count'] > 0
                
                if not exists:
                    return {"success": False, "error": "Product not found"}
                
                # Build update query
                update_data = {k: v for k, v in product_data.dict().items() if v is not None}
                update_data['updated_at'] = datetime.now().isoformat()
                
                # Create SET clauses dynamically
                set_clauses = []
                params = {'product_id': product_id}
                
                for key, value in update_data.items():
                    set_clauses.append(f"p.{key} = ${key}")
                    params[key] = value
                
                update_query = f"""
                MATCH (p:Product {{id: $product_id}})
                SET {', '.join(set_clauses)}
                RETURN p
                """
                
                result = session.run(update_query, params)
                updated_product = dict(result.single()['p'])
                
                # Update brand and category relationships if needed
                if 'brand' in update_data:
                    session.run("""
                        MATCH (p:Product {id: $product_id})-[r:MANUFACTURED_BY]->()
                        DELETE r
                    """, {'product_id': product_id})
                    
                    session.run("""
                        MATCH (p:Product {id: $product_id})
                        MERGE (b:Brand {name: $brand})
                        MERGE (p)-[:MANUFACTURED_BY]->(b)
                    """, {'product_id': product_id, 'brand': update_data['brand']})
                
                if 'category' in update_data:
                    session.run("""
                        MATCH (p:Product {id: $product_id})-[r:BELONGS_TO]->()
                        DELETE r
                    """, {'product_id': product_id})
                    
                    session.run("""
                        MATCH (p:Product {id: $product_id})
                        MERGE (c:Category {name: $category})
                        MERGE (p)-[:BELONGS_TO]->(c)
                    """, {'product_id': product_id, 'category': update_data['category']})
                
                return {"success": True, "data": updated_product}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product from Neo4j"""
        try:
            with self.driver.session() as session:
                # Check if product exists
                check_query = "MATCH (p:Product {id: $product_id}) RETURN count(p) as count"
                check_result = session.run(check_query, {'product_id': product_id})
                exists = check_result.single()['count'] > 0
                
                if not exists:
                    return {"success": False, "error": "Product not found"}
                
                # Delete product and its relationships
                delete_query = """
                MATCH (p:Product {id: $product_id})
                DETACH DELETE p
                """
                
                session.run(delete_query, {'product_id': product_id})
                return {"success": True, "message": "Product deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_products(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Search products with filters in Neo4j"""
        try:
            with self.driver.session() as session:
                # Build query based on filters
                where_clauses = []
                params = {}
                
                if filters.category and filters.category.lower() != 'all':
                    where_clauses.append("p.category = $category")
                    params['category'] = filters.category
                
                if filters.brand and filters.brand.lower() != 'all':
                    where_clauses.append("p.brand = $brand")
                    params['brand'] = filters.brand
                
                if filters.min_price:
                    where_clauses.append("p.price >= $min_price")
                    params['min_price'] = filters.min_price
                
                if filters.max_price:
                    where_clauses.append("p.price <= $max_price")
                    params['max_price'] = filters.max_price
                
                # Build the query
                query = "MATCH (p:Product)"
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
                
                query += " RETURN p ORDER BY p.id"
                
                result = session.run(query, params)
                products = []
                
                for record in result:
                    product_data = dict(record['p'])
                    
                    # Apply keyword search (client-side filtering)
                    if filters.keywords:
                        keywords = filters.keywords.lower().split(',')
                        keywords = [kw.strip() for kw in keywords if kw.strip()]
                        
                        # Check if any keyword matches name or description
                        product_text = f"{product_data.get('name', '')} {product_data.get('description', '')}".lower()
                        
                        keyword_match = False
                        for keyword in keywords:
                            if keyword in product_text:
                                keyword_match = True
                                break
                        
                        if not keyword_match:
                            continue
                    
                    products.append(product_data)
                
                return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get all unique categories from Neo4j"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Category)
                RETURN c.name as category
                ORDER BY c.name
                """
                
                result = session.run(query)
                categories = []
                
                for record in result:
                    categories.append(record['category'])
                
                return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_brands(self) -> List[str]:
        """Get all unique brands from Neo4j"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (b:Brand)
                RETURN b.name as brand
                ORDER BY b.name
                """
                
                result = session.run(query)
                brands = []
                
                for record in result:
                    brands.append(record['brand'])
                
                return brands
        except Exception as e:
            print(f"Error getting brands: {e}")
            return []
    
    def _get_next_product_id(self, session) -> int:
        """Get next available product ID"""
        try:
            query = """
            MATCH (p:Product)
            RETURN max(p.id) as max_id
            """
            
            result = session.run(query)
            record = result.single()
            max_id = record['max_id'] if record and record['max_id'] is not None else 0
            
            return max_id + 1
        except Exception as e:
            print(f"Error getting next product ID: {e}")
            return 1

# Global service instance
product_service = Neo4jProductService()
