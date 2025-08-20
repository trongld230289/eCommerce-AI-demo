import json
import asyncio
import os
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
from services.ai_service import AIService
from product_service import product_service
import openai
from models import Product

# Constants
TOP_K = 5
EMBEDDING_MODEL = "text-embedding-3-small"
GENERATION_MODEL = "gpt-4o-mini"

# Cache for LLM results to avoid duplicate calls
_category_cache = {}
_upgrade_cache = {}

def get_openai_client():
    """Get OpenAI client instance"""
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class WishlistRecommendationRAG:
    def __init__(self, my_items: List[Product], shared_items: List[Product], user_product_ids: List[int]):
        self.client = get_openai_client()
        self.my_items = my_items
        self.shared_items = shared_items
        self.user_product_ids = set(user_product_ids)  # Convert to set for faster lookup

        # Filter out shared items that are also in user's wishlist to avoid self-recommendation
        filtered_shared_items = []
        print(f"DEBUG: User product IDs to filter out: {self.user_product_ids}")
        for item in shared_items:
            print(f"DEBUG: Checking shared item - ID: {item.id} (type: {type(item.id)}), Name: {getattr(item, 'name', 'N/A')}")
            # Convert both to int to ensure proper comparison
            item_id = int(item.id) if item.id else None
            if item_id and item_id not in {int(pid) for pid in self.user_product_ids if pid is not None}:
                filtered_shared_items.append(item)
            else:
                print(f"DEBUG: ❌ FILTERED OUT item ID {item.id} as it matches user's product or is invalid")
        
        self.shared_items = filtered_shared_items
        print(f"Filtered shared items: {len(self.shared_items)} (removed {len(shared_items) - len(filtered_shared_items)} duplicates)")

        if not self.shared_items:
            print("No shared items available after filtering duplicates")
            return

        # Build index over shared items
        shared_texts = [p.as_text() for p in self.shared_items]
        self.shared_vectors = embed_texts(self.client, shared_texts)

        if not self.shared_vectors:
            print("No embeddings generated for shared items")
            return

        dim = len(self.shared_vectors[0])
        self.index = faiss.IndexFlatIP(dim)  # cosine via normalized vectors
        # Normalize vectors
        shared_matrix = np.vstack(self.shared_vectors).astype("float32")
        faiss.normalize_L2(shared_matrix)
        self.index.add(shared_matrix)

    def retrieve(self, query: Product, k: int = TOP_K) -> List[Tuple[Product, float]]:
        q_vec = embed_texts(self.client, [query.as_text()])[0].reshape(1, -1).astype("float32")
        faiss.normalize_L2(q_vec)
        scores, idx = self.index.search(q_vec, k)
        results = []
        for j, score in zip(idx[0], scores[0]):
            if j == -1:
                continue
            results.append((self.shared_items[j], float(score)))
        return results

    def recommend(self, lang: str = "en") -> Dict[str, Any]:
        outputs: Dict[str, Any] = {"recommendations": []}
        for item in self.my_items:
            neighbors = self.retrieve(item, k=TOP_K)
            suggestion = generate_suggestion(self.client, item, neighbors, lang=lang)
            outputs["recommendations"].append(
                {
                    "query": item.title or item.name,
                    "neighbors": [{"title": p.title or p.name, "score": round(s, 3)} for p, s in neighbors],
                    "suggestion": suggestion,
                }
            )
        return outputs

def generate_suggestion(client: Any, my_item: Product, neighbors: List[Tuple[Product, float]], lang: str = "en") -> str:
    """
    Use an LLM to produce a short, warm suggestion based on retrieved neighbors.
    Simplified version - just generate generic suggestion text.
    """
    if not neighbors:
        return f"No alternatives found for {my_item.name} in shared wishlists."
    
    # Filter neighbors to same category for LLM context (lightweight check)
    same_category_neighbors = []
    for prod, score in neighbors:
        if prod.id != my_item.id and basic_category_match(my_item, prod):
            same_category_neighbors.append((prod, score))
    
    # If no same category neighbors, return generic message
    if not same_category_neighbors:
        return f"No {my_item.category} alternatives found in shared wishlists."
    
    # Take the top same-category neighbor for context (simple approach)
    top_neighbor = same_category_neighbors[0][0]
    
    neighbor_lines = [
        f"- {prod.title or prod.name} (score={score:.3f})" for prod, score in same_category_neighbors[:2]  # Only top 2
    ]
    context = f"""
User's wishlist item:
- {my_item.as_text()}

Related {my_item.category} products from shared wishlists:
{chr(10).join(neighbor_lines)}
"""

    if client is None:
        # Simple fallback logic
        return f'Consider upgrading your {my_item.category} with "{top_neighbor.title or top_neighbor.name}"!'

    system = (
        f"You are a helpful shopping assistant. "
        f"Write exactly ONE concise sentence (<= 25 English words) "
        f"recommending a {my_item.category} product upgrade or alternative. "
        f"Focus on the most relevant same-category option."
    )

    user = (
        f"{context}\n\n"
        f"Based on the {my_item.category} product '{my_item.title or my_item.name}' "
        f"write one short sentence recommending a {my_item.category} upgrade."
    )

    try:
        resp = client.chat.completions.create(
            model=GENERATION_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM suggestion generation failed: {e}")
        return f'Consider upgrading your {my_item.category} with "{top_neighbor.title or top_neighbor.name}"!'


def embed_texts(client: Any, texts: List[str]) -> List[np.ndarray]:
    """
    Return list of float32 numpy vectors.
    If client is None (no API key), returns improved similarity-based embeddings
    that consider product categories and brands for better matching.
    """
    if client is None:
        # Improved fallback embeddings that consider semantic similarity
        def smart_embed(t: str, dim: int = 384) -> np.ndarray:
            # Create base embedding from hash
            rng = np.random.default_rng(abs(hash(t)) % (2**32))
            v = rng.standard_normal(dim).astype("float32")
            
            # Boost similarity for same categories/brands
            category_words = ['phone', 'laptop', 'tablet', 'watch', 'iphone', 'macbook', 'ipad']
            brand_words = ['apple', 'samsung', 'dell']
            
            # Add category and brand features
            for i, word in enumerate(category_words):
                if word in t.lower():
                    v[i % dim] += 2.0  # Boost category dimensions
            
            for i, word in enumerate(brand_words):
                if word in t.lower():
                    v[(i + 50) % dim] += 1.5  # Boost brand dimensions
                    
            # Add model/version similarity
            if any(model in t.lower() for model in ['15', '16', 'm2', 'm3']):
                v[100 % dim] += 1.0
            
            v /= np.linalg.norm(v) + 1e-8
            return v
        return [smart_embed(t) for t in texts]

    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [np.array(d.embedding, dtype="float32") for d in resp.data]


def find_best_related_product(my_item: Product, neighbors: List[Tuple[Product, float]]) -> Tuple[Product, float]:
    """
    Enhanced logic with LLM to find the best related product within same category.
    Strict category filtering - only same category products allowed.
    """
    print(f"🔍 Finding best match for: {my_item.name} (Category: {my_item.category})")
    
    # First, strictly filter neighbors by same category only AND exclude self
    same_category_neighbors = []
    for prod, score in neighbors:
        print(f"  📋 Checking neighbor: {prod.name} (Category: {prod.category}) - Score: {score:.3f}")
        
        # Skip if it's the same product (avoid self-comparison)
        if prod.id == my_item.id:
            print(f"  🚫 SKIPPING - Same product ID ({prod.id})")
            continue
        
        # Quick category check first (no LLM needed for exact matches)
        if my_item.category and prod.category and my_item.category.lower() == prod.category.lower():
            same_category_neighbors.append((prod, score))
            print(f"  ✅ SAME CATEGORY - Added to candidates (exact match)")
            continue
            
        # Use LLM only for ambiguous cases
        if are_same_product_category(my_item, prod):
            same_category_neighbors.append((prod, score))
            print(f"  ✅ SAME CATEGORY - Added to candidates (LLM verified)")
        else:
            print(f"  ❌ DIFFERENT CATEGORY - Rejected")
    
    print(f"📊 Found {len(same_category_neighbors)} same-category candidates out of {len(neighbors)} total")
    
    # STRICT POLICY: Only return same category products
    if not same_category_neighbors:
        print("⚠️  NO SAME CATEGORY MATCHES - Returning None to skip this recommendation")
        # Return None to indicate no recommendation should be made
        return (None, 0.0)
    
    # Find best match within same category
    best_product = same_category_neighbors[0]  # Default to highest scored
    best_relevance = 0.0
    
    for prod, score in same_category_neighbors:
        relevance = score
        prod_text = prod.as_text().lower()
        my_text = my_item.as_text().lower()
        
        # Major boost for exact same category
        my_category = (my_item.category or "").lower()
        prod_category = (prod.category or "").lower()
        if my_category and prod_category and my_category == prod_category:
            relevance += 1.0
            
        # Boost same brand within same category
        my_brand = (my_item.brand or "").lower()
        prod_brand = (prod.brand or "").lower()
        if my_brand and prod_brand and my_brand == prod_brand:
            relevance += 0.8
        
        # Specific product type matching with LLM
        if is_upgrade_product(my_item, prod):
            relevance += 0.6
            
        # Prefer newer model numbers
        my_nums = [int(x) for x in my_text.split() if x.isdigit()]
        prod_nums = [int(x) for x in prod_text.split() if x.isdigit()]
        if my_nums and prod_nums and max(prod_nums) > max(my_nums):
            relevance += 0.4
            
        # Higher price often indicates upgrade
        if prod.price > my_item.price:
            relevance += 0.2
        
        print(f"  📈 {prod.name}: Final relevance = {relevance:.3f}")
        
        if relevance > best_relevance:
            best_relevance = relevance
            best_product = (prod, score)
    
    print(f"🎯 BEST MATCH: {best_product[0].name} (Score: {best_product[1]:.3f}, Relevance: {best_relevance:.3f})")
    return best_product

def are_same_product_category(item1: Product, item2: Product) -> bool:
    """Use LLM to determine if two products are in the same category with caching"""
    # Create cache key
    cache_key = f"{item1.category}_{item2.category}_{item1.name}_{item2.name}"
    
    # Check cache first
    if cache_key in _category_cache:
        return _category_cache[cache_key]
    
    # Quick fallback for exact category match
    if item1.category and item2.category and item1.category.lower() == item2.category.lower():
        _category_cache[cache_key] = True
        return True
    
    try:
        client = get_openai_client()
        if not client:
            result = basic_category_match(item1, item2)
            _category_cache[cache_key] = result
            return result
            
        prompt = f"""
Are these two products in the same category? Answer with just "YES" or "NO".

Product 1: {item1.name} - Category: {item1.category}
Product 2: {item2.name} - Category: {item2.category}

Our system has exactly 5 categories. Products should ONLY be considered the same category if they match these exact rules:

1. **Phone**: iPhone, Samsung Galaxy, Android phones, smartphones - Category: "Phone"
2. **Camera**: Canon, Sony, Fuji, DSLR, mirrorless cameras - Category: "Camera"  
3. **Watch**: Apple Watch, Samsung Watch, smartwatches - Category: "Watch"
4. **Camping Gear**: Tents, sleeping bags, outdoor equipment - Category: "Camping Gear"
5. **Laptop**: MacBook, Dell, HP laptops, computers - Category: "Laptop"

IMPORTANT RULES:
- Phone ≠ Camera (NEVER recommend cameras for phone users)
- Camera ≠ Phone (NEVER recommend phones for camera users)
- Each category is completely separate
- Only answer YES if both products are clearly in the exact same category

Answer:"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        answer = resp.choices[0].message.content.strip().upper()
        result = answer == "YES"
        _category_cache[cache_key] = result
        return result
        
    except Exception as e:
        print(f"LLM category check failed: {e}")
        result = basic_category_match(item1, item2)
        _category_cache[cache_key] = result
        return result

def is_upgrade_product(my_item: Product, candidate: Product) -> bool:
    """Use LLM to determine if candidate is an upgrade of my_item. Cached results."""
    global _upgrade_cache
    
    # Create cache key
    cache_key = f"{my_item.category}_{my_item.name}_{candidate.category}_{candidate.name}"
    
    # Check cache first
    if cache_key in _upgrade_cache:
        result = _upgrade_cache[cache_key]
        print(f"🎯 UPGRADE CACHE HIT: {result}")
        return result
    
    try:
        client = get_openai_client()
        if not client:
            _upgrade_cache[cache_key] = False
            return False
            
        prompt = f"""
Is Product 2 a good upgrade or alternative to Product 1? Answer with just "YES" or "NO".

Product 1 (Current): {my_item.name} - ${my_item.price}
Product 2 (Candidate): {candidate.name} - ${candidate.price}

Consider it an upgrade/good alternative if:
- Same product type but newer/better model (iPhone 14 → iPhone 15)
- Higher specs or better features  
- Professional version of consumer product
- More premium tier of same brand
- Complementary products in same category (sleeping pad + sleeping bag for camping)
- Related gear that serves similar purpose (camping equipment, camera accessories)

Answer:"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        answer = resp.choices[0].message.content.strip().upper()
        result = answer == "YES"
        
        # Cache the result
        _upgrade_cache[cache_key] = result
        print(f"🔄 UPGRADE LLM: {result} (cached)")
        
        return result
        
    except Exception as e:
        print(f"LLM upgrade check failed: {e}")
        # Cache the fallback result too
        _upgrade_cache[cache_key] = False
        return False

def basic_category_match(item1: Product, item2: Product) -> bool:
    """Fallback category matching without LLM"""
    cat1 = (item1.category or "").lower()
    cat2 = (item2.category or "").lower()
    
    # Exact category match first
    if cat1 == cat2:
        return True
    
    # Normalize to our 5 main categories
    def normalize_category(cat_text: str, item_name: str) -> str:
        combined = f"{cat_text} {item_name}".lower()
        
        if any(k in combined for k in ['phone', 'iphone', 'galaxy', 'smartphone', 'android']):
            return 'phone'
        elif any(k in combined for k in ['camera', 'canon', 'sony', 'fuji', 'dslr', 'mirrorless']):
            return 'camera'
        elif any(k in combined for k in ['watch', 'smartwatch', 'apple watch']):
            return 'watch'
        elif any(k in combined for k in ['camping', 'tent', 'sleeping bag', 'outdoor']):
            return 'camping gear'
        elif any(k in combined for k in ['laptop', 'macbook', 'computer', 'notebook']):
            return 'laptop'
        
        return cat_text.lower()
    
    norm_cat1 = normalize_category(cat1, item1.name)
    norm_cat2 = normalize_category(cat2, item2.name)
    
    return norm_cat1 == norm_cat2


def dict_to_product(product_dict: Dict[str, Any]) -> Product:
    """Convert product dictionary to Product model"""
    return Product(
        id=product_dict.get('id'),
        name=product_dict.get('name', ''),
        title=product_dict.get('name', ''),  # Use name as title
        price=product_dict.get('price', 0),
        original_price=product_dict.get('original_price', product_dict.get('actual_price')),  # Map original_price from actual_price
        category=product_dict.get('category', ''),
        description=product_dict.get('description', ''),
        brand=product_dict.get('brand', ''),
        rating=product_dict.get('rating', 4.0),
        imageUrl=product_dict.get('imageUrl', ''),
        tags=product_dict.get('tags', [])
    )


class WishlistRecommendationsService:
    def __init__(self):
        self.ai_service = AIService()
        # Initialize OpenAI client for embeddings
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-3-small"
    
    async def get_recommendations(self, user_id: str, all_product_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get embedding-based recommendations using WishlistRecommendationRAG.
        Enhanced version with async support and duplicate filtering.
        
        Args:
            user_id: User's ID (used to exclude their shared wishlists)
            all_product_ids: All product IDs from ALL user's wishlist tabs combined
        
        Returns:
            List of recommendations with suggestions
        """
        try:
            print("=== ENHANCED WISHLIST RECOMMENDATION RAG ===")
            print(f"User ID: {user_id}")
            print(f"Total Product IDs from all tabs: {len(all_product_ids)}")
            
            # Remove duplicates while preserving order
            unique_product_ids = list(dict.fromkeys(all_product_ids))
            print(f"Unique Product IDs: {len(unique_product_ids)}")
            
            # Get user's products (my_items) - call API once for all products
            my_items_dict = await self._get_products_by_ids_async(unique_product_ids)
            my_items = [dict_to_product(p) for p in my_items_dict]
            print(f"My items found: {len(my_items)}")
            
            if not my_items:
                print("No user products found, returning empty recommendations")
                return []
            
            # Get shared wishlist products (exclude current user's shared wishlists)
            shared_items_dict = await self._get_shared_products_excluding_user_async(user_id)
            shared_items = [dict_to_product(p) for p in shared_items_dict]
            print(f"Shared items found (excluding user {user_id}): {len(shared_items)}")
            
            if not shared_items:
                print("No shared wishlist products found, returning empty recommendations")
                return []
            
            # Create RAG instance with enhanced filtering
            rag = WishlistRecommendationRAG(my_items, shared_items, unique_product_ids)
            
            if not hasattr(rag, 'index') or not rag.shared_items:
                print("No recommendations possible after filtering")
                return []
                
            result = rag.recommend(lang="en")
            
            # Transform RAG output to API format
            recommendations = []
            for i, recommendation in enumerate(result["recommendations"]):
                if i >= len(my_items):
                    continue
                    
                # Get the original product details
                original_product = my_items[i]
                
                # Get the best recommended product from neighbors
                recommended_product = self._extract_recommended_product(recommendation, rag.shared_items, original_product)
                
                # Skip if no valid recommendation found (None returned)
                if recommended_product is None:
                    print(f"⏭️  Skipping recommendation for {original_product.name} - no same-category alternatives found")
                    continue
                
                # Build the recommendation in expected format
                formatted_recommendation = {
                    "query": recommendation["query"],
                    "product_query_id": original_product.id,
                    "suggestion": recommendation["suggestion"],
                    "product_suggestion": recommended_product
                }
                recommendations.append(formatted_recommendation)
            
            print(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            print(f"Error in get_recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    def _extract_recommended_product(self, recommendation: Dict[str, Any], shared_items: List[Product], original_product: Product) -> Optional[Dict[str, Any]]:
        """Extract recommended product from recommendation result with strict category matching"""
        print(f"🎯 EXTRACT: Processing recommendation for {original_product.name} (ID: {original_product.id})")
        
        if recommendation.get("neighbors"):
            print(f"📋 EXTRACT: Found {len(recommendation['neighbors'])} neighbors")
            
            # Convert neighbors to Product tuples for enhanced matching
            neighbor_products = []
            for neighbor in recommendation["neighbors"]:
                neighbor_title = neighbor["title"]
                neighbor_score = neighbor.get("score", 0.0)
                print(f"  🔍 EXTRACT: Looking for neighbor '{neighbor_title}' in {len(shared_items)} shared items")
                
                # Find the actual Product object in shared_items
                for shared_item in shared_items:
                    if (shared_item.title == neighbor_title or shared_item.name == neighbor_title):
                        neighbor_products.append((shared_item, neighbor_score))
                        print(f"  ✅ EXTRACT: Found match - {shared_item.name} (ID: {shared_item.id}, Category: {shared_item.category})")
                        break
                else:
                    print(f"  ❌ EXTRACT: No match found for neighbor '{neighbor_title}'")
            
            print(f"📊 EXTRACT: Converted {len(neighbor_products)} neighbors to Product objects")
            
            if neighbor_products:
                # Use enhanced logic to find best same-category match
                print(f"🔍 EXTRACT: Calling find_best_related_product...")
                best_match_result = find_best_related_product(original_product, neighbor_products)
                best_match_product, best_score = best_match_result
                
                # If find_best_related_product returns None (no same category found), skip this recommendation
                if best_match_product is None:
                    print(f"⚠️  EXTRACT: No same-category match found - skipping recommendation")
                    return None  # Return None to indicate no recommendation
                
                print(f"🎯 EXTRACT: Best match result - Product: {best_match_product.name} (ID: {best_match_product.id}), Score: {best_score}")
                
                # Additional safety check - don't recommend the same product
                if best_match_product.id == original_product.id or best_match_product is original_product:
                    print(f"⚠️  EXTRACT: Same product returned - skipping recommendation")
                    return None  # Return None to indicate no recommendation
                
                print(f"✅ EXTRACT: Returning different product recommendation: {best_match_product.name}")
                return {
                    "id": best_match_product.id,
                    "name": best_match_product.name,
                    "price": best_match_product.price,
                    "original_price": getattr(best_match_product, 'original_price', None),
                    "category": best_match_product.category,
                    "imageUrl": best_match_product.imageUrl,
                    "description": best_match_product.description,
                    "rating": best_match_product.rating,
                    "discount": getattr(best_match_product, 'discount', None)
                }
        
        # Fallback - no neighbors found, skip this recommendation
        print(f"⚠️  EXTRACT: No neighbors found - skipping recommendation")
        return None  # Return None to indicate no recommendation

    async def _get_products_by_ids_async(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Async version: Get products by their IDs from product service - call API once for all products"""
        try:
            print(f"Fetching {len(product_ids)} products in single batch...")
            
            # Use asyncio.gather to fetch all products concurrently
            tasks = [self._get_single_product_async(product_id) for product_id in product_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            products = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Error fetching product {product_ids[i]}: {result}")
                    continue
                if result:
                    products.append(result)
            
            print(f"Successfully retrieved {len(products)} products out of {len(product_ids)} requested")
            return products
            
        except Exception as e:
            print(f"Error in batch product fetch: {str(e)}")
            return []

    async def _get_single_product_async(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Async wrapper for single product fetch"""
        try:
            # Since product_service is sync, we'll run it in a thread pool
            loop = asyncio.get_event_loop()
            product = await loop.run_in_executor(None, product_service.get_product_by_id, product_id)
            
            if not product:
                return None
                
            # Handle both dict and object types
            if isinstance(product, dict):
                return {
                    "id": product.get("id") or product.get("productId"),
                    "name": product.get("name", ""),
                    "price": product.get("price", 0),
                    "original_price": product.get("original_price"),
                    "category": product.get("category", ""),
                    "description": product.get("description", ""),
                    "brand": product.get("brand", ""),
                    "rating": product.get("rating", 4.0),
                    "imageUrl": product.get("imageUrl", "") or product.get("image", ""),
                }
            else:
                # Handle object type
                return {
                    "id": getattr(product, 'id', None) or getattr(product, 'productId', None),
                    "name": getattr(product, 'name', ''),
                    "price": getattr(product, 'price', 0),
                    "original_price": getattr(product, 'original_price', None),
                    "category": getattr(product, 'category', ''),
                    "description": getattr(product, 'description', ''),
                    "brand": getattr(product, 'brand', ''),
                    "rating": getattr(product, 'rating', 4.0),
                    "imageUrl": getattr(product, 'imageUrl', '') or getattr(product, 'image', ''),
                }
                
        except Exception as e:
            print(f"Error fetching product {product_id}: {str(e)}")
            return None

    async def _get_shared_products_excluding_user_async(self, excluded_user_id: str) -> List[Dict[str, Any]]:
        """Async version: Get shared wishlist products excluding current user's shared wishlists"""
        try:
            print(f"Fetching shared products excluding user: {excluded_user_id}")
            
            # Import here to avoid circular import
            from services.wishlist_service import wishlist_service
            
            # Get all shared wishlists (with user filtering at service level)
            loop = asyncio.get_event_loop()
            shared_wishlists = await loop.run_in_executor(None, wishlist_service.get_shared_wishlists, excluded_user_id)
            
            print(f"Found {len(shared_wishlists)} total shared wishlists")
            
            # Filter out wishlists belonging to the current user
            other_users_wishlists = []
            for wishlist in shared_wishlists:
                wishlist_user_id = getattr(wishlist, 'user_id', 'unknown_user')
                wishlist_name = getattr(wishlist, 'name', 'Unknown')
                
                print(f"DEBUG: Checking wishlist '{wishlist_name}' from user '{wishlist_user_id}' vs excluded '{excluded_user_id}'")
                print(f"DEBUG: User ID types - wishlist: {type(wishlist_user_id)}, excluded: {type(excluded_user_id)}")
                print(f"DEBUG: Exact comparison - '{wishlist_user_id}' == '{excluded_user_id}': {wishlist_user_id == excluded_user_id}")
                print(f"DEBUG: String comparison - '{str(wishlist_user_id)}' == '{str(excluded_user_id)}': {str(wishlist_user_id) == str(excluded_user_id)}")
                
                # Use string comparison to be safe
                if str(wishlist_user_id) != str(excluded_user_id):
                    print(f"✅ INCLUDING wishlist '{wishlist_name}' from user {wishlist_user_id}")
                    other_users_wishlists.append(wishlist)
                else:
                    print(f"❌ EXCLUDING wishlist '{wishlist_name}' from user {wishlist_user_id}")
            
            print(f"After excluding user {excluded_user_id}: {len(other_users_wishlists)} wishlists remain")
            
            if not other_users_wishlists:
                print("No shared wishlists from other users found")
                return []
            
            # Collect all products from other users' shared wishlists
            shared_products = []
            for wishlist in other_users_wishlists:
                if hasattr(wishlist, 'products') and wishlist.products:
                    for product_item in wishlist.products:
                        if hasattr(product_item, 'product_details') and product_item.product_details:
                            product_details = product_item.product_details
                            # Handle both dict and object types
                            if isinstance(product_details, dict):
                                product_dict = {
                                    "id": product_details.get("id") or product_details.get("productId"),
                                    "name": product_details.get("name", ""),
                                    "price": product_details.get("price", 0),
                                    "original_price": product_details.get("original_price"),
                                    "category": product_details.get("category", ""),
                                    "description": product_details.get("description", ""),
                                    "brand": product_details.get("brand", ""),
                                    "rating": product_details.get("rating", 4.0),
                                    "imageUrl": product_details.get("imageUrl", "") or product_details.get("image", ""),
                                }
                            else:
                                # Handle object type
                                product_dict = {
                                    "id": getattr(product_details, 'id', None) or getattr(product_details, 'productId', None),
                                    "name": getattr(product_details, 'name', ''),
                                    "price": getattr(product_details, 'price', 0),
                                    "original_price": getattr(product_details, 'original_price', None),
                                    "category": getattr(product_details, 'category', ''),
                                    "description": getattr(product_details, 'description', ''),
                                    "brand": getattr(product_details, 'brand', ''),
                                    "rating": getattr(product_details, 'rating', 4.0),
                                    "imageUrl": getattr(product_details, 'imageUrl', '') or getattr(product_details, 'image', ''),
                                }
                            
                            if product_dict["id"]:
                                shared_products.append(product_dict)
            
            print(f"Collected {len(shared_products)} products from other users' shared wishlists")
            return shared_products
            
        except Exception as e:
            print(f"Error fetching shared products excluding user: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        """Get products by their IDs from product service"""
        try:
            products = []
            for product_id in product_ids:
                product = product_service.get_product_by_id(product_id)
                if product:
                    # Handle both dict and object types
                    if isinstance(product, dict):
                        product_dict = {
                            "id": product.get("id") or product.get("productId"),
                            "name": product.get("name", ""),
                            "price": product.get("price", 0),
                            "original_price": product.get("original_price"),  # Add original_price
                            "category": product.get("category", ""),
                            "description": product.get("description", ""),
                            "brand": product.get("brand", ""),
                            "rating": product.get("rating", 4.0),
                            "imageUrl": product.get("imageUrl") or product.get("image", ""),
                        }
                    else:
                        # Handle object type
                        product_dict = {
                            "id": getattr(product, 'id', None) or getattr(product, 'productId', None),
                            "name": getattr(product, 'name', ''),
                            "price": getattr(product, 'price', 0),
                            "original_price": getattr(product, 'original_price', None),  # Add original_price
                            "category": getattr(product, 'category', ''),
                            "description": getattr(product, 'description', ''),
                            "brand": getattr(product, 'brand', ''),
                            "rating": getattr(product, 'rating', 4.0),
                            "imageUrl": getattr(product, 'imageUrl', '') or getattr(product, 'image', ''),
                        }
                    
                    if product_dict["id"] and product_dict["name"]:
                        products.append(product_dict)
            return products
        except Exception as e:
            print(f"Error getting products by IDs: {str(e)}")
            return []
    
    def _get_shared_products_from_service(self) -> List[Dict[str, Any]]:
        """Get products from shared wishlists"""
        try:
            from services.wishlist_service import wishlist_service
            
            print("Getting shared wishlist products from public/anonymous wishlists...")
            
            # Get all shared wishlists (status = 'public' or 'anonymous')
            shared_wishlists = wishlist_service.get_shared_wishlists()
            print(f"Found {len(shared_wishlists)} shared wishlists")
            
            # Extract unique product_ids from shared wishlists
            shared_product_ids = set()
            
            for wishlist in shared_wishlists:
                # Handle Wishlist object attributes instead of dict methods
                user_id = getattr(wishlist, 'user_id', 'unknown_user')
                products = getattr(wishlist, 'products', [])
                share_status = getattr(wishlist, 'share_status', 'private')
                
                print(f"Processing wishlist from user {user_id} with share_status '{share_status}' and {len(products)} products")
                
                # Check both string and enum values for share_status
                is_shared = (
                    share_status == 'public' or 
                    share_status == 'anonymous' or
                    str(share_status) == 'public' or 
                    str(share_status) == 'anonymous' or
                    (hasattr(share_status, 'value') and share_status.value in ['public', 'anonymous'])
                )
                
                print(f"Is shared wishlist: {is_shared}")
                
                # Only process public or anonymous wishlists
                if is_shared:
                    # Extract product IDs from product objects
                    for product in products:
                        product_id = None
                        if hasattr(product, 'product_id'):
                            product_id = product.product_id
                        elif isinstance(product, dict) and 'product_id' in product:
                            product_id = product['product_id']
                        
                        if product_id:
                            shared_product_ids.add(product_id)
                else:
                    print(f"Skipping private wishlist from user {user_id}")
            
            print(f"Found {len(shared_product_ids)} unique products from shared wishlists")
            
            # Get product metadata for each shared product_id
            shared_products = []
            for product_id in shared_product_ids:
                try:
                    product = product_service.get_product_by_id(product_id)
                    if product:
                        # Handle both dict and object types
                        if isinstance(product, dict):
                            product_dict = {
                                "id": product.get("id") or product.get("productId"),
                                "name": product.get("name", ""),
                                "price": product.get("price", 0),
                                "original_price": product.get("original_price"),  # Add original_price
                                "category": product.get("category", ""),
                                "description": product.get("description", ""),
                                "brand": product.get("brand", ""),
                                "rating": product.get("rating", 4.0),
                                "imageUrl": product.get("imageUrl") or product.get("image", ""),
                            }
                        else:
                            # Handle object type
                            product_dict = {
                                "id": getattr(product, 'id', None) or getattr(product, 'productId', None),
                                "name": getattr(product, 'name', ''),
                                "price": getattr(product, 'price', 0),
                                "original_price": getattr(product, 'original_price', None),  # Add original_price
                                "category": getattr(product, 'category', ''),
                                "description": getattr(product, 'description', ''),
                                "brand": getattr(product, 'brand', ''),
                                "rating": getattr(product, 'rating', 4.0),
                                "imageUrl": getattr(product, 'imageUrl', '') or getattr(product, 'image', ''),
                            }
                        
                        if product_dict["id"] and product_dict["name"]:
                            shared_products.append(product_dict)
                            
                except Exception as e:
                    print(f"Error getting product {product_id}: {str(e)}")
                    continue
            
            print(f"Successfully retrieved {len(shared_products)} shared wishlist products")
            return shared_products
            
        except Exception as e:
            print(f"Error getting shared wishlist products: {str(e)}")
            return []


# Global instance
wishlist_recommendations_service = WishlistRecommendationsService()
