from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Optional
import requests
import logging
import os
import uuid

# Try to import Chroma DB, fall back to mock if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  Chroma DB not available, using fallback storage")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BE_API_URL = "http://localhost:8000"  # Backend API URL  
CHROMA_PORT = 8001  # Port for this recommendation service

# Chroma DB Configuration
CHROMA_DB_PATH = "./chroma_db"  # Local path for Chroma DB storage
COLLECTION_NAME = "user_events"  # Collection name for user events
PRODUCTS_COLLECTION_NAME = "product_embeddings"  # Collection name for product embeddings

class ChromaEventStore:
    """Chroma DB integration for storing and retrieving user events"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.fallback_storage = {}  # Fallback storage when Chroma is not available
        
        if CHROMA_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
                self.collection = self.client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"description": "User interaction events for recommendation system"}
                )
                logger.info("✅ Chroma DB initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Chroma DB: {e}")
                self.client = None
                self.collection = None
        else:
            logger.warning("⚠️ Chroma DB not available, using fallback storage")
    
    def store_event(self, event: Dict[str, Any]) -> bool:
        """Store user event in Chroma DB or fallback storage"""
        try:
            if self.collection:
                # Store in Chroma DB
                event_text = self._create_event_embedding_text(event)
                logger.info(f"💾 Storing event in Chroma DB: {event['id']} for user {event['user_id']}")
                logger.info(f"📝 Event text: {event_text}")
                logger.info(f"📋 Event metadata: {event}")
                
                # Flatten metadata for Chroma DB (only primitive types allowed)
                flattened_metadata = {
                    'id': event['id'],
                    'user_id': event['user_id'],
                    'event_type': event['event_type'],
                    'product_id': event['product_id'],
                    'timestamp': event['timestamp']
                }
                
                # Flatten product_data if it exists
                if 'product_data' in event and isinstance(event['product_data'], dict):
                    for key, value in event['product_data'].items():
                        if isinstance(value, (str, int, float, bool)):
                            flattened_metadata[f'product_{key}'] = value
                        else:
                            flattened_metadata[f'product_{key}'] = str(value)
                
                # Add other metadata fields if they exist
                if 'metadata' in event and isinstance(event['metadata'], dict):
                    for key, value in event['metadata'].items():
                        if isinstance(value, (str, int, float, bool)):
                            flattened_metadata[f'meta_{key}'] = value
                        else:
                            flattened_metadata[f'meta_{key}'] = str(value)
                
                logger.info(f"🔄 Flattened metadata: {flattened_metadata}")
                
                self.collection.add(
                    documents=[event_text],
                    metadatas=[flattened_metadata],
                    ids=[event["id"]]
                )
                logger.info(f"✅ Event stored successfully in Chroma DB")
                return True
            else:
                # Store in fallback storage
                logger.info(f"📂 Storing event in fallback storage for user {event['user_id']}")
                user_id = event["user_id"]
                if user_id not in self.fallback_storage:
                    self.fallback_storage[user_id] = []
                self.fallback_storage[user_id].append(event)
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing event: {e}")
            # Try fallback storage
            user_id = event["user_id"]
            if user_id not in self.fallback_storage:
                self.fallback_storage[user_id] = []
            self.fallback_storage[user_id].append(event)
            return True
    
    def get_user_events(self, user_id: str, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get user events from Chroma DB or fallback storage"""
        try:
            if self.collection:
                # Query Chroma DB for user events
                where_clause = {"user_id": user_id}
                if event_type:
                    where_clause["event_type"] = event_type
                
                logger.info(f"🔍 Querying Chroma DB with where clause: {where_clause}")
                
                results = self.collection.get(
                    where=where_clause,
                    limit=limit if limit > 0 else None
                )
                
                logger.info(f"📊 Chroma DB query results: {len(results['ids'])} events found")
                
                # Convert results back to event format
                events = []
                for i, doc_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i]
                    logger.info(f"📄 Event {i}: {metadata}")
                    
                    # Reconstruct original event structure from flattened metadata
                    event = {
                        'id': metadata.get('id'),
                        'user_id': metadata.get('user_id'),
                        'event_type': metadata.get('event_type'),
                        'product_id': metadata.get('product_id'),
                        'timestamp': metadata.get('timestamp'),
                        'product_data': {},
                        'metadata': {}
                    }
                    
                    # Reconstruct product_data and metadata from flattened fields
                    for key, value in metadata.items():
                        if key.startswith('product_'):
                            event['product_data'][key[8:]] = value  # Remove 'product_' prefix
                        elif key.startswith('meta_'):
                            event['metadata'][key[5:]] = value  # Remove 'meta_' prefix
                    
                    events.append(event)
                
                return events
            else:
                # Get from fallback storage
                logger.info(f"📂 Using fallback storage for user {user_id}")
                user_events = self.fallback_storage.get(user_id, [])
                if event_type:
                    user_events = [e for e in user_events if e.get("event_type") == event_type]
                return user_events[-limit:] if limit > 0 else user_events
                
        except Exception as e:
            logger.error(f"❌ Error getting user events: {e}")
            # Fallback to in-memory storage
            user_events = self.fallback_storage.get(user_id, [])
            if event_type:
                user_events = [e for e in user_events if e.get("event_type") == event_type]
            return user_events[-limit:] if limit > 0 else user_events
    
    def delete_user_event(self, user_id: str, event_id: str) -> bool:
        """Delete a specific user event"""
        try:
            if self.collection:
                # Delete from Chroma DB
                self.collection.delete(ids=[event_id])
                return True
            else:
                # Delete from fallback storage
                if user_id in self.fallback_storage:
                    self.fallback_storage[user_id] = [
                        e for e in self.fallback_storage[user_id] 
                        if e.get("id") != event_id
                    ]
                return True
                
        except Exception as e:
            logger.error(f"❌ Error deleting event: {e}")
            return False
    
    def delete_all_user_events(self, user_id: str) -> int:
        """Delete all events for a user"""
        try:
            if self.collection:
                # Get all event IDs for the user
                results = self.collection.get(where={"user_id": user_id})
                event_ids = results["ids"]
                
                if event_ids:
                    self.collection.delete(ids=event_ids)
                    return len(event_ids)
                return 0
            else:
                # Fallback storage
                if user_id in self.fallback_storage:
                    count = len(self.fallback_storage[user_id])
                    del self.fallback_storage[user_id]
                    return count
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error deleting user events: {e}")
            return 0
    
    def find_similar_events(self, user_id: str, query_text: str, limit: int = 10) -> List[Dict]:
        """Find similar events using vector similarity search"""
        try:
            if self.collection:
                results = self.collection.query(
                    query_texts=[query_text],
                    where={"user_id": user_id},
                    n_results=limit
                )
                
                # Convert results to event format
                events = []
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    events.append(metadata)
                
                return events
            else:
                # Simple text matching for fallback
                user_events = self.fallback_storage.get(user_id, [])
                query_lower = query_text.lower()
                matched_events = []
                
                for event in user_events:
                    event_text = self._create_event_embedding_text(event).lower()
                    if query_lower in event_text:
                        matched_events.append(event)
                
                return matched_events[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error finding similar events: {e}")
            return []
    
    def _create_event_embedding_text(self, event: Dict[str, Any]) -> str:
        """Create text representation of event for embedding"""
        product_data = event.get("product_data", {})
        return f"User {event['event_type']} action on {product_data.get('name', '')} {product_data.get('category', '')} {product_data.get('brand', '')} price {product_data.get('price', 0)}"

class SemanticProductSearch:
    """Semantic product search using embeddings and cosine similarity"""
    
    def __init__(self):
        self.client = None
        self.products_collection = None
        self.products_cache = {}
        self.embeddings_initialized = False
        
        if CHROMA_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
                self.products_collection = self.client.get_or_create_collection(
                    name=PRODUCTS_COLLECTION_NAME,
                    metadata={"description": "Product embeddings for semantic search"}
                )
                logger.info("✅ Semantic Product Search initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Semantic Product Search: {e}")
                self.client = None
                self.products_collection = None
        else:
            logger.warning("⚠️ Semantic Product Search not available without Chroma DB")
    
    def create_product_embedding_text(self, product: Dict[str, Any]) -> str:
        """Create a comprehensive text representation for embedding"""
        # Combine all searchable product information
        text_parts = []
        
        # Product name
        if product.get("name"):
            text_parts.append(product["name"])
        
        # Category
        if product.get("category"):
            text_parts.append(product["category"])
        
        # Brand
        if product.get("brand"):
            text_parts.append(product["brand"])
        
        # Description
        if product.get("description"):
            text_parts.append(product["description"])
        
        # Specifications
        if product.get("specifications"):
            if isinstance(product["specifications"], dict):
                for key, value in product["specifications"].items():
                    text_parts.append(f"{key}: {value}")
            else:
                text_parts.append(str(product["specifications"]))
        
        # Tags or keywords
        if product.get("tags"):
            if isinstance(product["tags"], list):
                text_parts.extend(product["tags"])
            else:
                text_parts.append(str(product["tags"]))
        
        # Price range indication
        price = product.get("price", 0)
        if price > 0:
            if price < 1000000:  # Under 1M VND
                text_parts.append("budget affordable cheap")
            elif price < 10000000:  # Under 10M VND
                text_parts.append("mid-range moderate")
            else:  # Over 10M VND
                text_parts.append("premium expensive high-end")
        
        return " ".join(text_parts).lower()
    
    def embed_all_products(self, products: List[Dict[str, Any]]) -> bool:
        """Embed all products and store in Chroma DB"""
        if not self.products_collection:
            logger.error("❌ Products collection not available")
            return False
        
        try:
            # Clear existing embeddings
            try:
                # Get all existing documents first
                existing_docs = self.products_collection.get()
                if existing_docs and existing_docs.get('ids'):
                    self.products_collection.delete(ids=existing_docs['ids'])
                    logger.info(f"🧹 Cleared {len(existing_docs['ids'])} existing embeddings")
                else:
                    logger.info("🧹 No existing embeddings to clear")
            except Exception as delete_error:
                logger.warning(f"⚠️ Could not clear existing embeddings: {delete_error}")
            
            # Prepare data for embedding
            documents = []
            metadatas = []
            ids = []
            
            logger.info(f"📦 Processing {len(products)} products for embedding")
            
            for product in products:
                product_id = str(product.get("id", product.get("product_id", "")))
                if not product_id or product_id == "":
                    logger.warning(f"⚠️ Skipping product with missing ID: {product.get('name', 'Unknown')}")
                    continue
                
                # Create embedding text
                embedding_text = self.create_product_embedding_text(product)
                
                if not embedding_text:
                    logger.warning(f"⚠️ Skipping product with empty embedding text: {product.get('name', 'Unknown')}")
                    continue
                
                # Prepare metadata
                metadata = {
                    "product_id": product_id,
                    "name": product.get("name", ""),
                    "category": product.get("category", ""),
                    "brand": product.get("brand", ""),
                    "price": float(product.get("price", 0)),
                    "rating": float(product.get("rating", 0)),
                    "featured": bool(product.get("featured", False))
                }
                
                documents.append(embedding_text)
                metadatas.append(metadata)
                ids.append(product_id)
                
                # Cache product data
                self.products_cache[product_id] = product
            
            # Store embeddings in Chroma DB
            if documents:
                logger.info(f"💾 Storing {len(documents)} documents in Chroma DB")
                logger.info(f"📝 Sample document: {documents[0][:100]}...")
                logger.info(f"🏷️ Sample metadata: {metadatas[0]}")
                
                self.products_collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                self.embeddings_initialized = True
                logger.info(f"✅ Successfully embedded {len(documents)} products")
                return True
            else:
                logger.warning("⚠️ No products to embed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error embedding products: {e}")
            return False
    
    def semantic_search(self, query: str, limit: int = 10, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings and cosine similarity"""
        if not self.products_collection or not self.embeddings_initialized:
            logger.error("❌ Products not embedded or collection not available")
            return []
        
        try:
            # Query similar products using embeddings
            results = self.products_collection.query(
                query_texts=[query.lower()],
                n_results=limit,
                include=['metadatas', 'distances', 'documents']
            )
            
            # Process results
            search_results = []
            
            for i, product_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                # Convert distance to similarity score (cosine similarity)
                similarity_score = 1 - distance
                
                # Filter by minimum similarity
                if similarity_score < min_similarity:
                    continue
                
                # Get full product data from cache
                product_data = self.products_cache.get(product_id, {})
                
                # Create result object
                result = {
                    "product_id": product_id,
                    "similarity_score": round(similarity_score, 4),
                    "product_data": product_data,
                    "matched_text": results["documents"][0][i] if results.get("documents") else "",
                    "metadata": metadata
                }
                
                search_results.append(result)
            
            # Sort by similarity score
            search_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"✅ Semantic search for '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}")
            return []
    
    def hybrid_search(self, query: str, limit: int = 10, semantic_weight: float = 0.7) -> List[Dict[str, Any]]:
        """Combine semantic search with traditional keyword matching"""
        semantic_results = self.semantic_search(query, limit * 2)  # Get more results for hybrid
        
        # Traditional keyword search results
        keyword_results = []
        query_lower = query.lower()
        
        for product_id, product in self.products_cache.items():
            # Simple keyword matching score
            keyword_score = 0.0
            product_text = self.create_product_embedding_text(product).lower()
            
            # Exact phrase match
            if query_lower in product_text:
                keyword_score += 1.0
            
            # Individual word matches
            query_words = query_lower.split()
            word_matches = sum(1 for word in query_words if word in product_text)
            keyword_score += (word_matches / len(query_words)) * 0.5
            
            if keyword_score > 0:
                keyword_results.append({
                    "product_id": product_id,
                    "keyword_score": keyword_score,
                    "product_data": product
                })
        
        # Combine results
        hybrid_results = {}
        
        # Add semantic results
        for result in semantic_results:
            product_id = result["product_id"]
            hybrid_results[product_id] = {
                **result,
                "semantic_score": result["similarity_score"],
                "keyword_score": 0.0,
                "hybrid_score": result["similarity_score"] * semantic_weight
            }
        
        # Add/update with keyword results
        for result in keyword_results:
            product_id = result["product_id"]
            if product_id in hybrid_results:
                hybrid_results[product_id]["keyword_score"] = result["keyword_score"]
                hybrid_results[product_id]["hybrid_score"] = (
                    hybrid_results[product_id]["semantic_score"] * semantic_weight +
                    result["keyword_score"] * (1 - semantic_weight)
                )
            else:
                hybrid_results[product_id] = {
                    "product_id": product_id,
                    "semantic_score": 0.0,
                    "keyword_score": result["keyword_score"],
                    "hybrid_score": result["keyword_score"] * (1 - semantic_weight),
                    "product_data": result["product_data"],
                    "similarity_score": 0.0
                }
        
        # Convert to list and sort by hybrid score
        final_results = list(hybrid_results.values())
        final_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        return final_results[:limit]
    
    def store_event(self, event: Dict[str, Any]) -> bool:
        """Store user event in Chroma DB or fallback storage"""
        try:
            if self.collection:
                # Create embedding-friendly text from event
                event_text = self._create_event_embedding_text(event)
                
                # Store in Chroma DB
                self.collection.add(
                    documents=[event_text],
                    metadatas=[{
                        "user_id": event["user_id"],
                        "event_type": event["event_type"],
                        "product_id": event["product_id"],
                        "timestamp": event["timestamp"],
                        "product_name": event.get("product_data", {}).get("name", ""),
                        "product_category": event.get("product_data", {}).get("category", ""),
                        "product_brand": event.get("product_data", {}).get("brand", ""),
                        "product_price": str(event.get("product_data", {}).get("price", 0))
                    }],
                    ids=[event["id"]]
                )
                logger.info(f"✅ Event {event['id']} stored in Chroma DB")
                return True
            else:
                # Fallback to in-memory storage
                user_id = event["user_id"]
                if user_id not in self.fallback_storage:
                    self.fallback_storage[user_id] = []
                self.fallback_storage[user_id].append(event)
                logger.info(f"✅ Event {event['id']} stored in fallback storage")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing event: {e}")
            # Try fallback storage
            user_id = event["user_id"]
            if user_id not in self.fallback_storage:
                self.fallback_storage[user_id] = []
            self.fallback_storage[user_id].append(event)
            return True
    
    def get_user_events(self, user_id: str, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get user events from Chroma DB or fallback storage"""
        try:
            if self.collection:
                # Query Chroma DB for user events
                results = self.collection.get(
                    where={"user_id": user_id} if not event_type else {"user_id": user_id, "event_type": event_type},
                    limit=limit
                )
                
                # Convert results back to event format
                events = []
                for i, doc_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i]
                    event = {
                        "id": doc_id,
                        "user_id": metadata["user_id"],
                        "event_type": metadata["event_type"],
                        "product_id": metadata["product_id"],
                        "timestamp": metadata["timestamp"],
                        "product_data": {
                            "name": metadata.get("product_name", ""),
                            "category": metadata.get("product_category", ""),
                            "brand": metadata.get("product_brand", ""),
                            "price": float(metadata.get("product_price", 0)) if metadata.get("product_price") != "0" else 0
                        }
                    }
                    events.append(event)
                
                return events
            else:
                # Fallback storage
                user_events = self.fallback_storage.get(user_id, [])
                if event_type:
                    user_events = [e for e in user_events if e["event_type"] == event_type]
                return user_events[-limit:] if limit > 0 else user_events
                
        except Exception as e:
            logger.error(f"❌ Error getting user events: {e}")
            # Fallback to in-memory storage
            user_events = self.fallback_storage.get(user_id, [])
            if event_type:
                user_events = [e for e in user_events if e["event_type"] == event_type]
            return user_events[-limit:] if limit > 0 else user_events
    
    def delete_user_event(self, user_id: str, event_id: str) -> bool:
        """Delete a specific user event"""
        try:
            if self.collection:
                self.collection.delete(ids=[event_id])
                logger.info(f"✅ Event {event_id} deleted from Chroma DB")
                return True
            else:
                # Fallback storage
                if user_id in self.fallback_storage:
                    events = self.fallback_storage[user_id]
                    self.fallback_storage[user_id] = [e for e in events if e["id"] != event_id]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting event: {e}")
            return False
    
    def delete_all_user_events(self, user_id: str) -> int:
        """Delete all events for a user"""
        try:
            if self.collection:
                # Get all user events first
                results = self.collection.get(where={"user_id": user_id})
                event_ids = results["ids"]
                
                if event_ids:
                    self.collection.delete(ids=event_ids)
                    logger.info(f"✅ Deleted {len(event_ids)} events for user {user_id}")
                    return len(event_ids)
                return 0
            else:
                # Fallback storage
                if user_id in self.fallback_storage:
                    count = len(self.fallback_storage[user_id])
                    del self.fallback_storage[user_id]
                    return count
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error deleting user events: {e}")
            return 0
    
    def find_similar_events(self, user_id: str, query_text: str, limit: int = 10) -> List[Dict]:
        """Find similar events using vector similarity search"""
        try:
            if self.collection:
                results = self.collection.query(
                    query_texts=[query_text],
                    where={"user_id": user_id},
                    n_results=limit
                )
                
                # Convert results to event format
                events = []
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    event = {
                        "id": doc_id,
                        "user_id": metadata["user_id"],
                        "event_type": metadata["event_type"],
                        "product_id": metadata["product_id"],
                        "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "product_data": {
                            "name": metadata.get("product_name", ""),
                            "category": metadata.get("product_category", ""),
                            "brand": metadata.get("product_brand", "")
                        }
                    }
                    events.append(event)
                
                return events
            else:
                # Simple text matching for fallback
                user_events = self.fallback_storage.get(user_id, [])
                query_lower = query_text.lower()
                matched_events = []
                
                for event in user_events:
                    product_data = event.get("product_data", {})
                    event_text = f"{product_data.get('name', '')} {product_data.get('category', '')} {product_data.get('brand', '')}".lower()
                    if query_lower in event_text:
                        event_copy = event.copy()
                        event_copy["similarity_score"] = 0.8  # Mock similarity score
                        matched_events.append(event_copy)
                
                return matched_events[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error finding similar events: {e}")
            return []
    
    def _create_event_embedding_text(self, event: Dict[str, Any]) -> str:
        """Create text representation of event for embedding"""
        product_data = event.get("product_data", {})
        return f"User {event['event_type']} action on {product_data.get('name', '')} {product_data.get('category', '')} {product_data.get('brand', '')} price {product_data.get('price', 0)}"

# Initialize Chroma Event Store
chroma_store = ChromaEventStore()

class RecommendationEngine:
    def __init__(self):
        self.products_cache = []
        self.last_cache_update = None
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
    
    def get_products_from_be(self) -> List[Dict]:
        """Fetch all products from the main BE API"""
        try:
            response = requests.get(f"{BE_API_URL}/products", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch products from BE: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching products from BE: {e}")
            return []
    
    def get_cached_products(self) -> List[Dict]:
        """Get products with caching"""
        now = datetime.now()
        if (not self.products_cache or 
            not self.last_cache_update or 
            now - self.last_cache_update > self.cache_duration):
            
            self.products_cache = self.get_products_from_be()
            self.last_cache_update = now
            logger.info(f"Updated products cache with {len(self.products_cache)} products")
        
        return self.products_cache
    
    def parse_search_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language search query into structured filters"""
        query_lower = query.lower()
        filters = {}
        
        # Extract brand
        brands = ["apple", "samsung", "dell", "hp", "lenovo", "asus", "sony", "lg", "xiaomi", "huawei"]
        for brand in brands:
            if brand in query_lower:
                filters["brand"] = brand.title()
                break
        
        # Extract category/product type
        categories = {
            "laptop": "Laptop",
            "phone": "Điện thoại",
            "smartphone": "Điện thoại", 
            "tablet": "Tablet",
            "headphone": "Tai nghe",
            "speaker": "Loa",
            "watch": "Đồng hồ",
            "camera": "Camera"
        }
        
        for keyword, category in categories.items():
            if keyword in query_lower:
                filters["category"] = category
                break
        
        # Extract price constraints
        price_patterns = [
            r"below (\d+)([km]?)",  # below 20m, below 1000k
            r"under (\d+)([km]?)",  # under 20m
            r"dưới (\d+)([km]?)",   # dưới 20m
            r"< (\d+)([km]?)",      # < 20m
            r"less than (\d+)([km]?)" # less than 20m
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2) if match.group(2) else ""
                
                # Convert to actual price
                if unit == "m":  # million
                    max_price = amount * 1000000
                elif unit == "k":  # thousand  
                    max_price = amount * 1000
                else:
                    max_price = amount
                
                filters["max_price"] = max_price
                break
        
        # Extract minimum price
        min_price_patterns = [
            r"above (\d+)([km]?)",  # above 10m
            r"over (\d+)([km]?)",   # over 10m  
            r"trên (\d+)([km]?)",   # trên 10m
            r"> (\d+)([km]?)",      # > 10m
            r"more than (\d+)([km]?)" # more than 10m
        ]
        
        for pattern in min_price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2) if match.group(2) else ""
                
                if unit == "m":
                    min_price = amount * 1000000
                elif unit == "k":
                    min_price = amount * 1000
                else:
                    min_price = amount
                
                filters["min_price"] = min_price
                break
        
        # Extract keywords for general search
        # Remove processed parts and get remaining keywords
        cleaned_query = query_lower
        if "brand" in filters:
            cleaned_query = cleaned_query.replace(filters["brand"].lower(), "")
        
        # Remove price and common words
        stop_words = ["i", "want", "buy", "a", "an", "the", "with", "price", "below", "above", "under", "over", "than", "less", "more"]
        keywords = [word for word in cleaned_query.split() if word not in stop_words and len(word) > 2]
        
        if keywords:
            filters["keywords"] = " ".join(keywords)
        
        logger.info(f"Parsed query '{query}' into filters: {filters}")
        return filters
    
    def filter_products(self, products: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter products based on search criteria"""
        filtered = products.copy()
        
        # Filter by brand
        if "brand" in filters:
            filtered = [p for p in filtered if p.get("brand", "").lower() == filters["brand"].lower()]
        
        # Filter by category
        if "category" in filters:
            filtered = [p for p in filtered if filters["category"].lower() in p.get("category", "").lower()]
        
        # Filter by price range
        if "min_price" in filters:
            filtered = [p for p in filtered if p.get("price", 0) >= filters["min_price"]]
        
        if "max_price" in filters:
            filtered = [p for p in filtered if p.get("price", 0) <= filters["max_price"]]
        
        # Filter by keywords in name or description
        if "keywords" in filters:
            keywords = filters["keywords"].lower()
            filtered = [p for p in filtered 
                       if keywords in p.get("name", "").lower() or 
                          keywords in p.get("description", "").lower()]
        
        return filtered
    
    def get_user_recommendations(self, user_id: str, limit: int = 8) -> List[Dict]:
        """Get personalized recommendations for a user based on their events"""
        products = self.get_cached_products()
        if not products:
            return []
        
        user_events = chroma_store.get_user_events(user_id)
        
        if not user_events:
            # No user history, return popular/featured products
            featured_products = [p for p in products if p.get("featured", False)]
            if featured_products:
                # Sort by rating and return top products
                featured_products.sort(key=lambda x: x.get("rating", 0), reverse=True)
                return featured_products[:limit]
            else:
                # Return random products if no featured products
                return random.sample(products, min(limit, len(products)))
        
        # Analyze user events to understand preferences
        user_preferences = self.analyze_user_preferences(user_events)
        
        # Score products based on user preferences
        scored_products = []
        for product in products:
            score = self.calculate_product_score(product, user_preferences)
            scored_products.append((product, score))
        
        # Sort by score and return top recommendations
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products[:limit]]
    
    def analyze_user_preferences(self, user_events: List[Dict]) -> Dict[str, Any]:
        """Analyze user events to extract preferences"""
        preferences = {
            "preferred_categories": {},
            "preferred_brands": {},
            "price_range": {"min": 0, "max": float('inf')},
            "view_count": 0,
            "purchase_count": 0
        }
        
        total_price = 0
        price_count = 0
        
        for event in user_events:
            event_type = event.get("event_type", "")
            product_data = event.get("product_data", {})
            
            # Count event types
            if event_type == "view":
                preferences["view_count"] += 1
            elif event_type == "purchase":
                preferences["purchase_count"] += 1
            
            # Analyze product preferences
            if product_data:
                category = product_data.get("category", "")
                brand = product_data.get("brand", "")
                price = product_data.get("price", 0)
                
                if category:
                    preferences["preferred_categories"][category] = preferences["preferred_categories"].get(category, 0) + 1
                
                if brand:
                    preferences["preferred_brands"][brand] = preferences["preferred_brands"].get(brand, 0) + 1
                
                if price > 0:
                    total_price += price
                    price_count += 1
        
        # Calculate average price preference
        if price_count > 0:
            avg_price = total_price / price_count
            preferences["price_range"]["min"] = avg_price * 0.5  # 50% below average
            preferences["price_range"]["max"] = avg_price * 2.0  # 200% above average
        
        return preferences
    
    def calculate_product_score(self, product: Dict, preferences: Dict) -> float:
        """Calculate relevance score for a product based on user preferences"""
        score = 0.0
        
        # Category preference score
        category = product.get("category", "")
        if category in preferences["preferred_categories"]:
            score += preferences["preferred_categories"][category] * 2.0
        
        # Brand preference score
        brand = product.get("brand", "")
        if brand in preferences["preferred_brands"]:
            score += preferences["preferred_brands"][brand] * 1.5
        
        # Price preference score
        price = product.get("price", 0)
        if preferences["price_range"]["min"] <= price <= preferences["price_range"]["max"]:
            score += 3.0
        
        # Product rating score
        rating = product.get("rating", 0)
        score += rating
        
        # Featured product bonus
        if product.get("featured", False):
            score += 1.0
        
        return score

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

# Initialize semantic search engine
semantic_search_engine = SemanticProductSearch()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Recommendation System is running",
        "service": "recommendation_system",
        "timestamp": datetime.now().isoformat()
    })

# CRUD Operations for User Events

@app.route('/user-events', methods=['POST'])
def create_user_event():
    """Create a new user event and store in Chroma DB"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["user_id", "event_type", "product_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = data["user_id"]
        event_type = data["event_type"]
        product_id = data["product_id"]
        
        # Create event object
        event = {
            "id": f"{user_id}_{product_id}_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "event_type": event_type,  # view, click, add_to_cart, purchase, etc.
            "product_id": product_id,
            "product_data": data.get("product_data", {}),
            "timestamp": datetime.now().isoformat(),
            "metadata": data.get("metadata", {})
        }
        
        # Store in Chroma DB
        success = chroma_store.store_event(event)
        
        if success:
            logger.info(f"Created event {event['id']} for user {user_id}")
        
        return jsonify({
            "message": "User event created successfully",
            "event_id": event["id"],
            "user_id": user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating user event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user-events/<user_id>', methods=['GET'])
def get_user_events(user_id: str):
    """Get all events for a specific user"""
    try:
        limit = request.args.get('limit', 100, type=int)
        event_type = request.args.get('event_type')  # Optional filter
        
        user_events = chroma_store.get_user_events(user_id, limit, event_type)
        
        return jsonify({
            "user_id": user_id,
            "events": user_events,
            "total_events": len(user_events)
        })
        
    except Exception as e:
        logger.error(f"Error fetching user events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user-events/<user_id>/<event_id>', methods=['DELETE'])
def delete_user_event(user_id: str, event_id: str):
    """Delete a specific user event"""
    try:
        success = chroma_store.delete_user_event(user_id, event_id)
        
        if success:
            logger.info(f"Deleted event {event_id} for user {user_id}")
            return jsonify({
                "message": "Event deleted successfully",
                "event_id": event_id
            })
        else:
            return jsonify({"error": "Event not found"}), 404
        
    except Exception as e:
        logger.error(f"Error deleting user event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user-events/<user_id>', methods=['DELETE'])
def delete_all_user_events(user_id: str):
    """Delete all events for a user"""
    try:
        deleted_count = chroma_store.delete_all_user_events(user_id)
        
        logger.info(f"Deleted all {deleted_count} events for user {user_id}")
        return jsonify({
            "message": f"Deleted {deleted_count} events for user {user_id}",
            "deleted_count": deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error deleting user events: {e}")
        return jsonify({"error": str(e)}), 500

# Recommendation Endpoints

@app.route('/recommendations/<user_id>', methods=['GET'])
def get_user_recommendations(user_id: str):
    """Get top 8 product recommendations for a user"""
    try:
        limit = request.args.get('limit', 8, type=int)
        
        recommendations = recommendation_engine.get_user_recommendations(user_id, limit)
        
        return jsonify({
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def smart_search():
    """Smart search with natural language query"""
    try:
        data = request.get_json()
        
        if "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data["query"]
        limit = data.get("limit", 10)
        
        # Parse the natural language query
        filters = recommendation_engine.parse_search_query(query)
        
        # Get all products
        products = recommendation_engine.get_cached_products()
        
        if not products:
            return jsonify({
                "query": query,
                "filters": filters,
                "results": [],
                "count": 0,
                "message": "No products available"
            })
        
        # Filter products based on parsed criteria
        filtered_products = recommendation_engine.filter_products(products, filters)
        
        # Sort by relevance (rating, featured status)
        filtered_products.sort(key=lambda x: (
            x.get("rating", 0),
            1 if x.get("featured", False) else 0
        ), reverse=True)
        
        # Apply limit
        results = filtered_products[:limit]
        
        return jsonify({
            "query": query,
            "parsed_filters": filters,
            "results": results,
            "count": len(results),
            "total_found": len(filtered_products),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in smart search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search/semantic', methods=['POST'])
def semantic_search_api():
    """Semantic search using embeddings and cosine similarity"""
    try:
        data = request.get_json()
        
        if "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data["query"]
        limit = data.get("limit", 10)
        min_similarity = data.get("min_similarity", 0.3)
        
        # Ensure products are embedded
        if not semantic_search_engine.embeddings_initialized:
            products = recommendation_engine.get_cached_products()
            if products:
                success = semantic_search_engine.embed_all_products(products)
                if not success:
                    return jsonify({"error": "Failed to initialize product embeddings"}), 500
            else:
                return jsonify({"error": "No products available for search"}), 500
        
        # Perform semantic search
        results = semantic_search_engine.semantic_search(query, limit, min_similarity)
        
        return jsonify({
            "query": query,
            "search_type": "semantic",
            "results": results,
            "count": len(results),
            "min_similarity": min_similarity,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search/hybrid', methods=['POST'])
def hybrid_search_api():
    """Hybrid search combining semantic and keyword matching"""
    try:
        data = request.get_json()
        
        if "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data["query"]
        limit = data.get("limit", 10)
        semantic_weight = data.get("semantic_weight", 0.7)
        
        # Validate semantic weight
        if not 0 <= semantic_weight <= 1:
            return jsonify({"error": "semantic_weight must be between 0 and 1"}), 400
        
        # Ensure products are embedded
        if not semantic_search_engine.embeddings_initialized:
            products = recommendation_engine.get_cached_products()
            if products:
                success = semantic_search_engine.embed_all_products(products)
                if not success:
                    return jsonify({"error": "Failed to initialize product embeddings"}), 500
            else:
                return jsonify({"error": "No products available for search"}), 500
        
        # Perform hybrid search
        results = semantic_search_engine.hybrid_search(query, limit, semantic_weight)
        
        return jsonify({
            "query": query,
            "search_type": "hybrid",
            "results": results,
            "count": len(results),
            "semantic_weight": semantic_weight,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/products/embed', methods=['POST'])
def embed_products_api():
    """Manually trigger product embedding process"""
    try:
        force_refresh = request.get_json().get("force_refresh", False) if request.get_json() else False
        
        # Get latest products
        products = recommendation_engine.get_cached_products()
        if not products:
            return jsonify({"error": "No products available to embed"}), 400
        
        # Embed products
        success = semantic_search_engine.embed_all_products(products)
        
        if success:
            return jsonify({
                "message": "Products embedded successfully",
                "total_products": len(products),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to embed products"}), 500
            
    except Exception as e:
        logger.error(f"Error embedding products: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search/status', methods=['GET'])
def search_status():
    """Get status of semantic search system"""
    try:
        status = {
            "chroma_available": CHROMA_AVAILABLE,
            "embeddings_initialized": semantic_search_engine.embeddings_initialized if semantic_search_engine else False,
            "products_in_cache": len(semantic_search_engine.products_cache) if semantic_search_engine else 0,
            "collection_available": semantic_search_engine.products_collection is not None if semantic_search_engine else False,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting search status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/analytics/user-stats/<user_id>', methods=['GET'])
def get_user_analytics(user_id: str):
    """Get analytics for a specific user"""
    try:
        user_events = chroma_store.get_user_events(user_id)
        
        # Calculate stats
        event_types = {}
        categories_viewed = {}
        brands_viewed = {}
        total_events = len(user_events)
        
        for event in user_events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            product_data = event.get("product_data", {})
            category = product_data.get("category", "unknown")
            brand = product_data.get("brand", "unknown")
            
            categories_viewed[category] = categories_viewed.get(category, 0) + 1
            brands_viewed[brand] = brands_viewed.get(brand, 0) + 1
        
        return jsonify({
            "user_id": user_id,
            "total_events": total_events,
            "event_types": event_types,
            "top_categories": dict(sorted(categories_viewed.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_brands": dict(sorted(brands_viewed.items(), key=lambda x: x[1], reverse=True)[:5]),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user-events/<user_id>/similar', methods=['POST'])
def find_similar_user_events(user_id: str):
    """Find similar events for a user using vector similarity search"""
    try:
        data = request.get_json()
        
        if not data.get('query'):
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        
        similar_events = chroma_store.find_similar_events(user_id, query, limit)
        
        return jsonify({
            "user_id": user_id,
            "query": query,
            "similar_events": similar_events,
            "count": len(similar_events),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error finding similar events: {e}")
        return jsonify({"error": str(e)}), 500

# Test endpoints for development

@app.route('/test/sample-events', methods=['POST'])
def create_sample_events():
    """Create sample events for testing"""
    try:
        sample_events = [
            {
                "user_id": "user123",
                "event_type": "view",
                "product_id": "1",
                "product_data": {"name": "iPhone 14", "category": "Điện thoại", "brand": "Apple", "price": 999}
            },
            {
                "user_id": "user123", 
                "event_type": "add_to_cart",
                "product_id": "1",
                "product_data": {"name": "iPhone 14", "category": "Điện thoại", "brand": "Apple", "price": 999}
            },
            {
                "user_id": "user456",
                "event_type": "view", 
                "product_id": "2",
                "product_data": {"name": "Dell XPS 13", "category": "Laptop", "brand": "Dell", "price": 1299}
            }
        ]
        
        created_events = []
        for event_data in sample_events:
            # Use the create_user_event logic
            user_id = event_data["user_id"]
            event = {
                "id": f"{user_id}_{event_data['product_id']}_{int(datetime.now().timestamp())}",
                **event_data,
                "timestamp": datetime.now().isoformat(),
                "metadata": {}
            }
            
            success = chroma_store.store_event(event)
            if success:
                created_events.append(event["id"])
        
        return jsonify({
            "message": f"Created {len(created_events)} sample events",
            "event_ids": created_events
        })
        
    except Exception as e:
        logger.error(f"Error creating sample events: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting eCommerce Recommendation System...")
    print(f"📍 Server will be available at: http://localhost:{CHROMA_PORT}")
    print(f"🔗 Connected to BE API at: {BE_API_URL}")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=CHROMA_PORT, debug=True)
