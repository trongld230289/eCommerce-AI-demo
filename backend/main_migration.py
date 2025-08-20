import os
import json
from neo4j import GraphDatabase

# Neo4j connection parameters
class ConnectionParams:
    def __init__(self):
        self.env = {
            "NEO4J_URI": os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", "neo4j"),
            "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", "password")
        }

# Neo4j driver and query execution
class Neo4jManager:
    def __init__(self, connection_params: ConnectionParams):
        self.driver = GraphDatabase.driver(
            connection_params.env["NEO4J_URI"],
            auth=(connection_params.env["NEO4J_USERNAME"], connection_params.env["NEO4J_PASSWORD"])
        )

    def close(self):
        self.driver.close()

    def run_query(self, query: str, params: dict = None):
        try:
            with self.driver.session() as session:
                session.run(query, params or {})
                print(f"Query executed successfully: {query}")
        except Exception as e:
            print(f"Error executing query: {str(e)}")

    def run_multiple_queries(self, queries: list):
        try:
            with self.driver.session() as session:
                for query in queries:
                    session.run(query)
                    print(f"Query executed successfully: {query}")
        except Exception as e:
            print(f"Error executing queries: {str(e)}")

def clear_database(neo4j_manager: Neo4jManager):
    """Clear all data from the Neo4j database."""
    clear_query = "MATCH (n) DETACH DELETE n;"
    neo4j_manager.run_query(clear_query)

def escape_quotes(data):
    if isinstance(data, str):
        return data.replace("'", "\\'")
    elif isinstance(data, list):
        return [escape_quotes(item) for item in data]
    return data

def create_product_nodes(neo4j_manager: Neo4jManager):
    """Create Product nodes from products.json with flattened gifting attributes."""
    try:
        with open("data/products.json", "r") as f:
            products = json.load(f)

        # Calculate giftingPriceRange based on price percentiles
        prices = [p['price'] for p in products if 'price' in p]
        prices_sorted = sorted(prices)
        n = len(prices_sorted)
        if n > 0:
            low_idx = max(0, int(n * 0.33) - 1)
            mid_idx = max(0, int(n * 0.66) - 1)
            low_threshold = prices_sorted[low_idx]
            mid_threshold = prices_sorted[mid_idx]
            for product in products:
                price = product.get('price', 0)
                if price <= low_threshold:
                    product['giftingPriceRange'] = 'low'
                elif price <= mid_threshold:
                    product['giftingPriceRange'] = 'mid'
                else:
                    product['giftingPriceRange'] = 'high'

        # Escape special characters
        escaped_products = [{k: escape_quotes(v) for k, v in product.items()} for product in products]

        create_query = """
            UNWIND $products AS product
            MERGE (p:Product {productId: toInteger(product.productId)})
            SET p.name = product.name,
                p.image = product.image,
                p.price = toFloat(product.price),
                p.description = product.description,
                p.tags = product.tags,
                p.targetGenders = product.targetGenders,
                p.giftingSymbolicValue = product.giftingSymbolicValue,
                p.giftingUtilitarianScore = toFloat(product.giftingUtilitarianScore),
                p.giftingPriceRange = product.giftingPriceRange,
                p.giftingCategories = product.giftingCategories,
                p.giftingNoveltyScore = toFloat(product.giftingNoveltyScore),
                p.giftingRelationshipTypes = product.giftingRelationshipTypes,
                p.giftingAltruismSuitability = product.giftingAltruismSuitability,
                p.giftingReciprocityFit = product.giftingReciprocityFit,
                p.giftingSelfGiftingSuitability = product.giftingSelfGiftingSuitability,
                p.giftingPowerSignaling = product.giftingPowerSignaling,
                p.created_at = toInteger(product.created_at),
                p.updated_at = toInteger(product.updated_at)
            RETURN COUNT(p) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"products": escaped_products})
            created_count = result.single()[0]
            print(f"Product nodes created successfully: {created_count} nodes created from products.json;")
    except FileNotFoundError:
        print("Error: products.json not found. Please ensure the file exists in the script directory.")
    except json.JSONDecodeError as e:
        print(f"Error decoding products.json: {str(e)}")
    except Exception as e:
        print(f"Error creating product nodes: {str(e)}")

def create_user_nodes(neo4j_manager: Neo4jManager):
    """Create User nodes from users.json."""
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)

        escaped_users = [{k: escape_quotes(v) for k, v in user.items()} for user in users]

        create_query = """
            UNWIND $users AS user
            MERGE (u:User {userId: user.userId})
            SET u.name = user.name,
                u.email = user.email
            RETURN COUNT(u) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"users": escaped_users})
            created_count = result.single()[0]
            print(f"User nodes created successfully: {created_count} nodes created from users.json;")
    except FileNotFoundError:
        print("Error: users.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding users.json: {str(e)}")
    except Exception as e:
        print(f"Error creating user nodes: {str(e)}")

def create_wishlist_nodes(neo4j_manager: Neo4jManager):
    """Create Wishlist nodes and OWNS_WISHLIST relationships from wishlists.json."""
    try:
        with open("data/wishlists.json", "r") as f:
            wishlists = json.load(f)

        escaped_wishlists = [{k: escape_quotes(v) for k, v in wl.items()} for wl in wishlists]

        create_query = """
            UNWIND $wishlists AS wl
            MERGE (w:Wishlist {wishlistId: wl.wishlistId})
            SET w.userId = wl.userId,
                w.name = wl.name,
                w.note = wl.note,
                w.preferredRelationshipTypes = wl.preferredRelationshipTypes,
                w.isHedonic = wl.isHedonic,
                w.isAltruistic = wl.isAltruistic,
                w.expectsReciprocity = wl.expectsReciprocity,
                w.isSurprising = wl.isSurprising,
                w.isSelfGifting = wl.isSelfGifting,
                w.createdAt = toInteger(wl.createdAt),
                w.updatedAt = toInteger(wl.updatedAt)
            WITH w, wl
            MATCH (u:User {userId: wl.userId})
            MERGE (u)-[r:OWNS_WISHLIST {createdAt: toInteger(wl.createdAt)}]->(w)
            RETURN COUNT(w) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"wishlists": escaped_wishlists})
            created_count = result.single()[0]
            print(f"Wishlist nodes and OWNS_WISHLIST relationships created successfully: {created_count} nodes created from wishlists.json;")
    except FileNotFoundError:
        print("Error: wishlists.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding wishlists.json: {str(e)}")
    except Exception as e:
        print(f"Error creating wishlist nodes: {str(e)}")

def create_wishlist_contains(neo4j_manager: Neo4jManager):
    """Create CONTAINS relationships for wishlists from wishlist_contains.json."""
    try:
        with open("data/wishlist_contains.json", "r") as f:
            contains = json.load(f)

        escaped_contains = [{k: escape_quotes(v) for k, v in c.items()} for c in contains]

        create_query = """
            UNWIND $contains AS c
            MATCH (w:Wishlist {wishlistId: c.wishlistId})
            MATCH (p:Product {productId: toInteger(c.productId)})
            MERGE (w)-[r:CONTAINS {addedAt: toFloat(c.addedAt)}]->(p)
            RETURN COUNT(r) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"contains": escaped_contains})
            created_count = result.single()[0]
            print(f"Wishlist CONTAINS relationships created successfully: {created_count} relationships created from wishlist_contains.json;")
    except FileNotFoundError:
        print("Error: wishlist_contains.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding wishlist_contains.json: {str(e)}")
    except Exception as e:
        print(f"Error creating wishlist contains relationships: {str(e)}")

def create_cart_nodes(neo4j_manager: Neo4jManager):
    """Create Cart nodes and HAS_CART relationships from carts.json."""
    try:
        with open("data/carts.json", "r") as f:
            carts = json.load(f)
            for cart in carts:
                if "cardId" in cart:
                    cart["cartId"] = cart.pop("cardId")

        escaped_carts = [{k: escape_quotes(v) for k, v in c.items()} for c in carts]

        create_query = """
            UNWIND $carts AS c
            MERGE (cart:Cart {cartId: c.cartId})
            SET cart.userId = c.userId
            WITH cart, c
            MATCH (u:User {userId: c.userId})
            MERGE (u)-[r:HAS_CART {createdAt: toInteger(c.createdAt), updatedAt: toInteger(c.updatedAt)}]->(cart)
            RETURN COUNT(cart) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"carts": escaped_carts})
            created_count = result.single()[0]
            print(f"Cart nodes and HAS_CART relationships created successfully: {created_count} nodes created from carts.json;")
    except FileNotFoundError:
        print("Error: carts.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding carts.json: {str(e)}")
    except Exception as e:
        print(f"Error creating cart nodes: {str(e)}")

def create_cart_contains(neo4j_manager: Neo4jManager):
    """Create CONTAINS relationships for carts from cart_contains.json."""
    try:
        with open("data/cart_contains.json", "r") as f:
            contains = json.load(f)
            for cont in contains:
                if "cardId" in cont:
                    cont["cartId"] = cont.pop("cardId")

        escaped_contains = [{k: escape_quotes(v) for k, v in c.items()} for c in contains]

        create_query = """
            UNWIND $contains AS c
            MATCH (cart:Cart {cartId: c.cartId})
            MATCH (p:Product {productId: toInteger(c.productId)})
            MERGE (cart)-[r:CONTAINS {addedAt: toFloat(c.added_at), quantity: toInteger(c.quantity)}]->(p)
            RETURN COUNT(r) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"contains": escaped_contains})
            created_count = result.single()[0]
            print(f"Cart CONTAINS relationships created successfully: {created_count} relationships created from cart_contains.json;")
    except FileNotFoundError:
        print("Error: cart_contains.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding cart_contains.json: {str(e)}")
    except Exception as e:
        print(f"Error creating cart contains relationships: {str(e)}")

def create_interaction_events(neo4j_manager: Neo4jManager):
    """Create InteractionEvent nodes and related relationships from interaction_events.json."""
    try:
        with open("data/interaction_events.json", "r") as f:
            events = json.load(f)

        escaped_events = [{k: escape_quotes(v) for k, v in e.items()} for e in events]

        create_query = """
            UNWIND $events AS e
            MERGE (ie:InteractionEvent {eventId: e.eventId})
            SET ie.eventType = e.eventType,
                ie.timestamp = toInteger(e.timestamp),
                ie.value = toInteger(e.value),
                ie.expiresAt = toInteger(e.expiresAt),
                ie.noveltyRating = toFloat(e.noveltyRating),
                ie.utilityRating = toFloat(e.utilityRating)
            WITH ie, e
            MATCH (u:User {userId: e.userId})
            MERGE (u)-[r1:INTERACTED_WITH {timestamp: toInteger(e.timestamp)}]->(ie)
            WITH ie, e
            MATCH (p:Product {productId: toInteger(e.productId)})
            MERGE (ie)-[r2:TARGETS]->(p)
            RETURN COUNT(ie) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"events": escaped_events})
            created_count = result.single()[0]
            print(f"InteractionEvent nodes and relationships created successfully: {created_count} nodes created from interaction_events.json;")
    except FileNotFoundError:
        print("Error: interaction_events.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding interaction_events.json: {str(e)}")
    except Exception as e:
        print(f"Error creating interaction events: {str(e)}")

def create_recommended_by_als(neo4j_manager: Neo4jManager):
    """Create RECOMMENDED_BY_ALS relationships from recommended_by_als.json."""
    try:
        with open("data/recommended_by_als.json", "r") as f:
            recs = json.load(f)

        escaped_recs = [{k: escape_quotes(v) for k, v in r.items()} for r in recs]

        create_query = """
            UNWIND $recs AS r
            MATCH (u:User {userId: r.userId})
            MATCH (p:Product {productId: toInteger(r.productId)})
            MERGE (u)-[rel:RECOMMENDED_BY_ALS {score: toFloat(r.score)}]->(p)
            RETURN COUNT(rel) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"recs": escaped_recs})
            created_count = result.single()[0]
            print(f"RECOMMENDED_BY_ALS relationships created successfully: {created_count} relationships created from recommended_by_als.json;")
    except FileNotFoundError:
        print("Error: recommended_by_als.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding recommended_by_als.json: {str(e)}")
    except Exception as e:
        print(f"Error creating recommended_by_als relationships: {str(e)}")

def create_recommended_by_pagerank(neo4j_manager: Neo4jManager):
    """Create RECOMMENDED_BY_PAGERANK relationships from recommended_by_pagerank.json."""
    try:
        with open("data/recommended_by_pagerank.json", "r") as f:
            recs = json.load(f)

        escaped_recs = [{k: escape_quotes(v) for k, v in r.items()} for r in recs]

        create_query = """
            UNWIND $recs AS r
            MATCH (u:User {userId: r.userId})
            MATCH (p:Product {productId: toInteger(r.productId)})
            MERGE (u)-[rel:RECOMMENDED_BY_PAGERANK {score: toFloat(r.score)}]->(p)
            RETURN COUNT(rel) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"recs": escaped_recs})
            created_count = result.single()[0]
            print(f"RECOMMENDED_BY_PAGERANK relationships created successfully: {created_count} relationships created from recommended_by_pagerank.json;")
    except FileNotFoundError:
        print("Error: recommended_by_pagerank.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding recommended_by_pagerank.json: {str(e)}")
    except Exception as e:
        print(f"Error creating recommended_by_pagerank relationships: {str(e)}")

def create_similar_to(neo4j_manager: Neo4jManager):
    """Create SIMILAR_TO relationships from similar_to.json."""
    try:
        with open("data/similar_to.json", "r") as f:
            sims = json.load(f)

        escaped_sims = [{k: escape_quotes(v) for k, v in s.items()} for s in sims]

        create_query = """
            UNWIND $sims AS s
            MATCH (p1:Product {productId: toInteger(s.productId1)})
            MATCH (p2:Product {productId: toInteger(s.productId2)})
            MERGE (p1)-[rel:SIMILAR_TO {score: toFloat(s.score)}]->(p2)
            RETURN COUNT(rel) AS created_count;
        """
        with neo4j_manager.driver.session() as session:
            result = session.run(create_query, {"sims": escaped_sims})
            created_count = result.single()[0]
            print(f"SIMILAR_TO relationships created successfully: {created_count} relationships created from similar_to.json;")
    except FileNotFoundError:
        print("Error: similar_to.json not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding similar_to.json: {str(e)}")
    except Exception as e:
        print(f"Error creating similar_to relationships: {str(e)}")

def initialize_schema_metadata(neo4j_manager: Neo4jManager):
    """Initialize SchemaMetadata nodes and relationships for the Product node."""
    schema_queries = [
        "CREATE (m:SchemaMetadata {type: 'NodeLabel', label: 'Product', description: 'Represents a product in the gifting recommendation system, storing details like ID, name, price, and gifting attributes.'});",
        "CREATE (m1:SchemaMetadata {type: 'Property', label: 'Product', property: 'productId', description: 'A unique identifier (long or integer) for each product in the database, used to distinguish individual items.'});",
        "CREATE (m2:SchemaMetadata {type: 'Property', label: 'Product', property: 'name', description: 'The human-readable name of the product (e.g., \\'Gold Necklace\\'), serving as a primary identifier for users.'});",
        "CREATE (m3:SchemaMetadata {type: 'Property', label: 'Product', property: 'image', description: 'A URL or binary reference to the product’s image, used for visual representation in the UI.'});",
        "CREATE (m4:SchemaMetadata {type: 'Property', label: 'Product', property: 'price', description: 'The monetary cost of the product, used for price range calculation and purchase decisions.'});",
        "CREATE (m5:SchemaMetadata {type: 'Property', label: 'Product', property: 'description', description: 'A textual description of the product (e.g., \\'Elegant gold necklace with heart pendant\\'), providing details for LLM analysis.'});",
        "CREATE (m6:SchemaMetadata {type: 'Property', label: 'Product', property: 'tags', description: 'A list of keywords or categories (e.g., [\\'birthday\\', \\'luxury\\']) associated with the product, aiding semantic search.'});",
        "CREATE (m7:SchemaMetadata {type: 'Property', label: 'Product', property: 'targetGenders', description: 'A list of gender categories (\\'female\\', \\'male\\', \\'unisex\\') the product is marketed toward, guiding gifting recommendations.'});",
        "CREATE (m8:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingSymbolicValue', description: 'A qualitative measure (\\'high\\', \\'medium\\', \\'low\\') of the product’s emotional or cultural significance as a gift.'});",
        "CREATE (m9:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingUtilitarianScore', description: 'A float (0-1) indicating the product’s practicality, refined by user behavior (e.g., frequent purchases increase score).'});",
        "CREATE (m10:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingPriceRange', description: 'A categorical label (\\'low\\', \\'mid\\', \\'high\\') derived from price percentiles, indicating cost tier.'});",
        "CREATE (m11:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingCategories', description: 'A list of product categories (e.g., [\\'jewelry\\', \\'electronics\\']), used for filtering and behavioral analysis.'});",
        "CREATE (m12:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingNoveltyScore', description: 'A float (0-1) reflecting the product’s uniqueness, adjusted by user novelty ratings and purchase frequency.'});",
        "CREATE (m13:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingRelationshipTypes', description: 'A list of relationship contexts (e.g., [\\'romantic\\', \\'family\\']) where the product is suitable as a gift, updated from user relationships.'});",
        "CREATE (m14:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingAltruismSuitability', description: 'A qualitative measure (\\'high\\', \\'medium\\', \\'low\\') of the product’s fit for selfless gifting.'});",
        "CREATE (m15:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingReciprocityFit', description: 'A qualitative measure (\\'high\\', \\'medium\\', \\'low\\') indicating if the product suits reciprocal gifting.'});",
        "CREATE (m16:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingSelfGiftingSuitability', description: 'A qualitative measure (\\'high\\', \\'medium\\', \\'low\\') for the product’s appropriateness as a self-gift.'});",
        "CREATE (m17:SchemaMetadata {type: 'Property', label: 'Product', property: 'giftingPowerSignaling', description: 'A qualitative measure (\\'high\\', \\'medium\\', \\'low\\') of the product’s ability to convey status or authority.'});",
        "UNWIND ['productId', 'name', 'image', 'price', 'description', 'tags', 'targetGenders', 'giftingSymbolicValue', 'giftingUtilitarianScore', 'giftingPriceRange', 'giftingCategories', 'giftingNoveltyScore', 'giftingRelationshipTypes', 'giftingAltruismSuitability', 'giftingReciprocityFit', 'giftingSelfGiftingSuitability', 'giftingPowerSignaling'] AS prop MATCH (p:Product), (m:SchemaMetadata {property: prop}) CREATE (p)-[:HAS_PROPERTY_METADATA]->(m);",
        "MATCH (p:Product), (m:SchemaMetadata {label: 'Product'}) CREATE (p)-[:HAS_METADATA]->(m);"
    ]
    neo4j_manager.run_multiple_queries(schema_queries)

def main():
    # Initialize connection
    connection_params = ConnectionParams()
    neo4j_manager = Neo4jManager(connection_params)

    try:
        # Clear existing database
        print("Clearing existing database...")
        clear_database(neo4j_manager)

        # Create product nodes from JSON first
        print("Creating product nodes from products.json...")
        create_product_nodes(neo4j_manager)

        print("Creating user nodes...")
        create_user_nodes(neo4j_manager)

        print("Creating wishlist nodes and relationships...")
        create_wishlist_nodes(neo4j_manager)

        print("Creating wishlist contains relationships...")
        create_wishlist_contains(neo4j_manager)

        print("Creating cart nodes and relationships...")
        create_cart_nodes(neo4j_manager)

        print("Creating cart contains relationships...")
        create_cart_contains(neo4j_manager)

        print("Creating interaction events and relationships...")
        create_interaction_events(neo4j_manager)

        print("Creating recommended by ALS relationships...")
        create_recommended_by_als(neo4j_manager)

        print("Creating recommended by PageRank relationships...")
        create_recommended_by_pagerank(neo4j_manager)

        print("Creating similar to relationships...")
        create_similar_to(neo4j_manager)

        # Initialize schema metadata after products are created
        print("Initializing schema metadata...")
        initialize_schema_metadata(neo4j_manager)

        print("Database cleared, product nodes created, and schema metadata initialized successfully.")
    finally:
        neo4j_manager.close()

if __name__ == "__main__":
    main()