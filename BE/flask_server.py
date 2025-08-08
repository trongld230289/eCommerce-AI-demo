from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import requests
from datetime import datetime, timedelta
from firebase_config import get_firestore_db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Recommendation System Configuration
RECOMMENDATION_API_URL = "http://localhost:8001"  # Recommendation System API

# Temporary setting to bypass Firebase for faster response
USE_FIREBASE = True  # Set to True to use Firebase data

# Firebase Firestore helper functions
def get_all_products_from_firestore():
    """Get all products from Firebase Firestore with aggressive timeout handling"""
    # Temporarily bypass Firebase to test if the issue is Firebase-related
    if not USE_FIREBASE:
        print("Firebase bypassed, returning sample data")
        return get_sample_products()
    
    try:
        db = get_firestore_db()
        if db is None:
            print("Database connection failed, returning sample data")
            return get_sample_products()
        
        print("Attempting to fetch products from Firestore...")
        products_ref = db.collection('products')
        # Very short timeout - fail fast
        docs = products_ref.get(timeout=2.0)  # 2 second timeout
        
        products = []
        for doc in docs:
            product = doc.to_dict()
            # Ensure ID is set properly
            product['id'] = int(doc.id)
            products.append(product)
        
        # If no products found, return sample data
        if not products:
            print("No products found in Firestore, returning sample data")
            return get_sample_products()
        
        print(f"Successfully fetched {len(products)} products from Firestore")
        return products
    except Exception as e:
        print(f"Error fetching products from Firestore: {e}")
        print("Returning sample data as fallback")
        return get_sample_products()

def get_sample_products():
    """Return sample products when Firebase is unavailable"""
    return [
        {
            "id": 1,
            "name": "Wireless Bluetooth Headphones",
            "price": 89.99,
            "original_price": 129.99,
            "category": "Electronics",
            "brand": "TechSound",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
            "rating": 4.5,
            "reviews": 128,
            "description": "Premium wireless headphones with noise cancellation",
            "featured": True,
            "weeklySales": 45,
            "weeklyViews": 1250
        },
        {
            "id": 2,
            "name": "Smart Fitness Watch",
            "price": 199.99,
            "original_price": 249.99,
            "category": "Electronics",
            "brand": "FitTech",
            "image": "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=500",
            "rating": 4.3,
            "reviews": 89,
            "description": "Advanced fitness tracking with heart rate monitor",
            "featured": True,
            "weeklySales": 32,
            "weeklyViews": 890
        },
        {
            "id": 3,
            "name": "Portable Speaker",
            "price": 59.99,
            "original_price": 79.99,
            "category": "Electronics",
            "brand": "SoundMax",
            "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500",
            "rating": 4.7,
            "reviews": 203,
            "description": "Waterproof portable speaker with amazing sound",
            "featured": False,
            "weeklySales": 67,
            "weeklyViews": 1580
        },
        {
            "id": 4,
            "name": "Laptop Stand",
            "price": 39.99,
            "original_price": 59.99,
            "category": "Accessories",
            "brand": "DeskPro",
            "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
            "rating": 4.2,
            "reviews": 156,
            "description": "Adjustable aluminum laptop stand for better ergonomics",
            "featured": False,
            "weeklySales": 28,
            "weeklyViews": 720
        },
        {
            "id": 5,
            "name": "Wireless Mouse",
            "price": 29.99,
            "original_price": 39.99,
            "category": "Accessories",
            "brand": "ClickTech",
            "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
            "rating": 4.4,
            "reviews": 92,
            "description": "Ergonomic wireless mouse with precision tracking",
            "featured": True,
            "weeklySales": 51,
            "weeklyViews": 1120
        },
        {
            "id": 6,
            "name": "USB-C Hub",
            "price": 49.99,
            "original_price": 69.99,
            "category": "Accessories",
            "brand": "ConnectPro",
            "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
            "rating": 4.6,
            "reviews": 174,
            "description": "Multi-port USB-C hub with HDMI and card readers",
            "featured": False,
            "weeklySales": 39,
            "weeklyViews": 950
        }
    ]

def get_product_by_id_from_firestore(product_id):
    """Get a specific product by ID from Firebase Firestore with timeout handling"""
    # Temporarily bypass Firebase to test if the issue is Firebase-related
    if not USE_FIREBASE:
        sample_products = get_sample_products()
        for product in sample_products:
            if product['id'] == int(product_id):
                return product
        return None
    
    try:
        db = get_firestore_db()
        if db is None:
            # Try to find product in sample data
            sample_products = get_sample_products()
            for product in sample_products:
                if product['id'] == int(product_id):
                    return product
            return None
        
        doc_ref = db.collection('products').document(str(product_id))
        doc = doc_ref.get(timeout=2.0)  # 2 second timeout
        
        if doc.exists:
            product = doc.to_dict()
            product['id'] = int(doc.id)
            return product
        else:
            # If not found in Firestore, check sample data
            sample_products = get_sample_products()
            for product in sample_products:
                if product['id'] == int(product_id):
                    return product
        return None
    except Exception as e:
        print(f"Error fetching product {product_id} from Firestore: {e}")
        # Try to find product in sample data as fallback
        sample_products = get_sample_products()
        for product in sample_products:
            if product['id'] == int(product_id):
                return product
        return None

# Recommendation System Integration Functions
def send_user_event_to_recommendation_system(user_id, event_type, product_data):
    """Send user event to the Recommendation System for tracking"""
    try:
        if not user_id or not event_type or not product_data:
            return False
            
        event_data = {
            "user_id": str(user_id),
            "event_type": event_type,  # view, click, add_to_cart, purchase
            "product_id": str(product_data.get('id', '')),
            "product_data": {
                "name": product_data.get('name', ''),
                "category": product_data.get('category', ''),
                "brand": product_data.get('brand', ''),
                "price": product_data.get('price', 0)
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "backend_api"
            }
        }
        
        response = requests.post(
            f"{RECOMMENDATION_API_URL}/user-events",
            json=event_data,
            timeout=2.0  # Short timeout to not block main API
        )
        
        if response.status_code == 201:
            print(f"✅ Event {event_type} sent to recommendation system for user {user_id}")
            return True
        else:
            print(f"❌ Failed to send event to recommendation system: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending event to recommendation system: {e}")
        return False

def get_user_recommendations_from_system(user_id, limit=5):
    """Get personalized recommendations from the Recommendation System"""
    try:
        response = requests.get(
            f"{RECOMMENDATION_API_URL}/recommendations/{user_id}",
            params={"limit": limit},
            timeout=3.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('recommendations', [])
        else:
            print(f"❌ Failed to get recommendations: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        return []

def smart_search_from_recommendation_system(query, limit=10):
    """Use the smart search feature from Recommendation System"""
    try:
        search_data = {
            "query": query,
            "limit": limit
        }
        
        response = requests.post(
            f"{RECOMMENDATION_API_URL}/search",
            json=search_data,
            timeout=3.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "results": data.get('results', []),
                "parsed_filters": data.get('parsed_filters', {}),
                "total_found": data.get('total_found', 0)
            }
        else:
            print(f"❌ Failed to perform smart search: {response.status_code}")
            return {"results": [], "parsed_filters": {}, "total_found": 0}
            
    except Exception as e:
        print(f"❌ Error performing smart search: {e}")
        return {"results": [], "parsed_filters": {}, "total_found": 0}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products from Firestore"""
    try:
        products = get_all_products_from_firestore()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products from Firestore"""
    try:
        limit = request.args.get('limit', 6, type=int)
        products = get_all_products_from_firestore()
        featured_products = [p for p in products if p.get('featured', False)]
        # Sort by rating for best featured products first
        featured_products.sort(key=lambda x: x['rating'], reverse=True)
        return jsonify(featured_products[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/top-this-week', methods=['GET'])
def get_top_products_this_week():
    """Get Top Products This Week based on views and sales from Firestore"""
    try:
        limit = request.args.get('limit', 6, type=int)
        products = get_all_products_from_firestore()
        
        # Calculate popularity score based on views and sales
        products_with_score = []
        for product in products:
            # Weight: 70% weekly sales, 30% weekly views (normalized)
            max_sales = max(p.get('weeklySales', 0) for p in products)
            max_views = max(p.get('weeklyViews', 0) for p in products)
            
            sales_score = (product.get('weeklySales', 0) / max_sales) * 0.7 if max_sales > 0 else 0
            views_score = (product.get('weeklyViews', 0) / max_views) * 0.3 if max_views > 0 else 0
            
            total_score = sales_score + views_score
            products_with_score.append((product, total_score))
        
        # Sort by score (highest first) and return top products
        products_with_score.sort(key=lambda x: x[1], reverse=True)
        top_products = [product for product, score in products_with_score[:limit]]
        
        return jsonify(top_products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID from Firestore"""
    try:
        product = get_product_by_id_from_firestore(product_id)
        if product:
            return jsonify(product)
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_products():
    """Search products with smart search capabilities"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        if query:
            # Use smart search from recommendation system
            search_result = smart_search_from_recommendation_system(query, limit)
            
            return jsonify({
                "query": query,
                "results": search_result["results"],
                "parsed_filters": search_result["parsed_filters"],
                "total_found": search_result["total_found"],
                "search_type": "smart_search"
            })
        else:
            # Return all products if no query
            products = get_all_products_from_firestore()
            return jsonify({
                "query": "",
                "results": products[:limit],
                "total_found": len(products),
                "search_type": "all_products"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique categories from Firestore products"""
    try:
        products = get_all_products_from_firestore()
        categories = list({p['category'] for p in products})
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/brands', methods=['GET'])
def get_brands():
    """Get all unique brands from Firestore products"""
    try:
        products = get_all_products_from_firestore()
        brands = list({p['brand'] for p in products})
        return jsonify(brands)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_recommendations():
    """Get personalized product recommendations using the Recommendation System"""
    try:
        limit = request.args.get('limit', 4, type=int)
        user_id = request.args.get('user_id')
        
        if user_id:
            # Get personalized recommendations from recommendation system
            recommendations = get_user_recommendations_from_system(user_id, limit)
            
            if recommendations:
                # Add recommendation metadata
                for product in recommendations:
                    product['recommendationReason'] = "Based on your preferences"
                    product['recommendationScore'] = round(random.uniform(0.8, 0.95), 2)
                    product['source'] = "recommendation_system"
                
                return jsonify(recommendations)
        
        # Fallback: Use traditional recommendation logic if no user_id or recommendation system unavailable
        products = get_all_products_from_firestore()
        
        # Simple recommendation algorithm: 
        # 1. Include some featured products
        # 2. Include some high-rated products
        # 3. Add some random variety
        
        featured_products = [p for p in products if p.get('featured', False)]
        high_rated_products = [p for p in products if p['rating'] >= 4.5]
        
        recommendations = []
        
        # Add 2 featured products
        if featured_products:
            recommendations.extend(random.sample(featured_products, min(2, len(featured_products))))
        
        # Add high-rated products to fill remaining slots
        remaining_slots = limit - len(recommendations)
        if remaining_slots > 0 and high_rated_products:
            # Remove already added products
            available_high_rated = [p for p in high_rated_products if p not in recommendations]
            if available_high_rated:
                recommendations.extend(random.sample(available_high_rated, min(remaining_slots, len(available_high_rated))))
        
        # If still need more, add random products
        remaining_slots = limit - len(recommendations)
        if remaining_slots > 0:
            available_products = [p for p in products if p not in recommendations]
            if available_products:
                recommendations.extend(random.sample(available_products, min(remaining_slots, len(available_products))))
        
        # Add recommendation metadata
        for product in recommendations:
            product['recommendationReason'] = "Popular products"
            product['recommendationScore'] = round(random.uniform(0.7, 0.85), 2)
            product['source'] = "fallback_algorithm"
        
        return jsonify(recommendations[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        for product in recommendations:
            product['recommendationReason'] = "Based on your preferences"
            product['recommendationScore'] = round(random.uniform(0.7, 0.95), 2)
        
        return jsonify(recommendations[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Event tracking functions
def save_user_event_to_firestore(event_data):
    """Save user event to Firebase Firestore with timeout handling"""
    try:
        db = get_firestore_db()
        if db is None:
            print("Database connection failed for event tracking")
            return None
        
        # Add server timestamp
        event_data['timestamp'] = datetime.now()
        
        # Add to events collection with timeout
        events_ref = db.collection('user_events')
        doc_ref = events_ref.add(event_data)
        
        return doc_ref[1].id  # Return the document ID
    except Exception as e:
        print(f"Error saving event to Firestore: {e}")
        return None

@app.route('/events', methods=['POST'])
def track_user_event():
    """Track user events like view, add to cart, etc."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_type', 'user_id', 'product_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate event type
        valid_event_types = ['view', 'add_to_cart', 'remove_from_cart', 'add_to_wishlist', 'remove_from_wishlist']
        if data['event_type'] not in valid_event_types:
            return jsonify({"error": f"Invalid event_type. Must be one of: {valid_event_types}"}), 400
        
        # Get product information for metadata if not provided
        product = get_product_by_id_from_firestore(data['product_id'])
        if 'metadata' not in data or not data['metadata']:
            if product:
                data['metadata'] = {
                    'product_name': product.get('name'),
                    'product_category': product.get('category'),
                    'product_brand': product.get('brand'),
                    'product_price': product.get('price'),
                    'device': 'web',  # Default to web
                    'source': 'unknown'  # Can be enhanced based on referrer
                }
            else:
                data['metadata'] = {'device': 'web', 'source': 'unknown'}
        
        # Save event to Firestore
        event_id = save_user_event_to_firestore(data)
        
        # Send to Recommendation System
        recommendation_success = False
        if product:
            recommendation_success = send_user_event_to_recommendation_system(
                data['user_id'], data['event_type'], product
            )
        
        if event_id:
            return jsonify({
                "success": True,
                "message": "Event tracked successfully",
                "event_id": event_id,
                "firebase_saved": True,
                "recommendation_system_sent": recommendation_success
            })
        else:
            return jsonify({"error": "Failed to save event"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/events/<user_id>', methods=['GET'])
def get_user_events(user_id):
    """Get events for a specific user"""
    try:
        db = get_firestore_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Query parameters
        limit = request.args.get('limit', 100, type=int)
        event_type = request.args.get('event_type')
        
        # Build query
        events_ref = db.collection('user_events').where('user_id', '==', user_id)
        
        if event_type:
            events_ref = events_ref.where('event_type', '==', event_type)
        
        # Order by timestamp descending and limit
        events_ref = events_ref.order_by('timestamp', direction='DESCENDING').limit(limit)
        
        # Execute query
        docs = events_ref.get()
        
        events = []
        for doc in docs:
            event = doc.to_dict()
            event['id'] = doc.id
            # Convert timestamp to ISO string if it exists
            if 'timestamp' in event and event['timestamp']:
                event['timestamp'] = event['timestamp'].isoformat()
            events.append(event)
        
        return jsonify({
            "success": True,
            "events": events,
            "count": len(events)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/events/analytics/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics summary for a user"""
    try:
        db = get_firestore_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get all events for user
        events_ref = db.collection('user_events').where('user_id', '==', user_id)
        docs = events_ref.get()
        
        # Process analytics
        analytics = {
            'total_events': 0,
            'events_by_type': {},
            'most_viewed_products': {},
            'most_viewed_categories': {},
            'cart_actions': 0,
            'wishlist_actions': 0
        }
        
        for doc in docs:
            event = doc.to_dict()
            analytics['total_events'] += 1
            
            event_type = event.get('event_type', 'unknown')
            analytics['events_by_type'][event_type] = analytics['events_by_type'].get(event_type, 0) + 1
            
            if event_type == 'view':
                product_id = event.get('product_id')
                analytics['most_viewed_products'][product_id] = analytics['most_viewed_products'].get(product_id, 0) + 1
                
                if event.get('metadata') and event['metadata'].get('product_category'):
                    category = event['metadata']['product_category']
                    analytics['most_viewed_categories'][category] = analytics['most_viewed_categories'].get(category, 0) + 1
            
            if event_type in ['add_to_cart', 'remove_from_cart']:
                analytics['cart_actions'] += 1
            
            if event_type in ['add_to_wishlist', 'remove_from_wishlist']:
                analytics['wishlist_actions'] += 1
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New Recommendation System Integration Endpoints

@app.route('/track-event', methods=['POST'])
def track_user_event_to_recommendation():
    """Track user event and send to both Firebase and Recommendation System"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('user_id') or not data.get('event_type'):
            return jsonify({"error": "Missing user_id or event_type"}), 400
        
        user_id = data['user_id']
        event_type = data['event_type']
        product_id = data.get('product_id')
        
        # Get product data if product_id provided
        product_data = {}
        if product_id:
            product = get_product_by_id_from_firestore(product_id)
            if product:
                product_data = product
        
        # Save to Firebase (existing logic)
        event_data = {
            'user_id': user_id,
            'event_type': event_type,
            'product_id': product_id,
            'product_name': product_data.get('name', ''),
            'product_category': product_data.get('category', ''),
            'product_price': product_data.get('price', 0),
            'session_id': data.get('session_id', ''),
            'metadata': data.get('metadata', {})
        }
        
        firebase_success = save_user_event_to_firestore(event_data)
        
        # Send to Recommendation System
        recommendation_success = False
        if product_data:
            recommendation_success = send_user_event_to_recommendation_system(
                user_id, event_type, product_data
            )
        
        return jsonify({
            "success": True,
            "firebase_saved": firebase_success is not None,
            "recommendation_system_sent": recommendation_success,
            "message": "Event tracked successfully"
        })
        
    except Exception as e:
        print(f"Error tracking user event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def get_smart_recommendations():
    """Get smart recommendations from the Recommendation System"""
    try:
        limit = request.args.get('limit', 4, type=int)
        user_id = request.args.get('user_id')
        
        recommendations = get_user_recommendations_from_system(user_id, limit)
        
        if recommendations:
            return jsonify({
                "user_id": user_id,
                "recommendations": recommendations,
                "count": len(recommendations),
                "source": "recommendation_system",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Fallback to traditional recommendations
            return get_recommendations()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/smart', methods=['POST'])
def smart_search():
    """Smart search using natural language processing"""
    try:
        data = request.get_json()
        
        if not data.get('query'):
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        
        # Use recommendation system's smart search
        search_result = smart_search_from_recommendation_system(query, limit)
        
        return jsonify({
            "query": query,
            "results": search_result["results"],
            "parsed_filters": search_result["parsed_filters"],
            "total_found": search_result["total_found"],
            "search_type": "smart_nlp_search",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/semantic', methods=['POST'])
def semantic_search():
    """Semantic search using embeddings and cosine similarity"""
    try:
        data = request.get_json()
        
        if not data.get('query'):
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        min_similarity = data.get('min_similarity', 0.3)
        
        # Call recommendation system's semantic search API
        rec_response = requests.post(
            f"{RECOMMENDATION_API_URL}/search/semantic",
            json={
                "query": query,
                "limit": limit,
                "min_similarity": min_similarity
            },
            timeout=10
        )
        
        if rec_response.status_code == 200:
            result = rec_response.json()
            # Transform results to match FE expectations
            products = []
            for item in result.get('results', []):
                product_data = item.get('product_data', {})
                # Add similarity score as metadata
                product_data['similarity_score'] = item.get('similarity_score', 0)
                products.append(product_data)
            
            return jsonify({
                "query": query,
                "results": products,
                "search_type": "semantic_embedding",
                "total_found": len(products),
                "min_similarity": min_similarity,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "error": "Recommendation system error",
                "details": rec_response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search/hybrid', methods=['POST'])
def hybrid_search():
    """Hybrid search combining semantic and keyword matching"""
    try:
        data = request.get_json()
        
        if not data.get('query'):
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        semantic_weight = data.get('semantic_weight', 0.7)
        
        # Call recommendation system's hybrid search API
        rec_response = requests.post(
            f"{RECOMMENDATION_API_URL}/search/hybrid",
            json={
                "query": query,
                "limit": limit,
                "semantic_weight": semantic_weight
            },
            timeout=10
        )
        
        if rec_response.status_code == 200:
            result = rec_response.json()
            # Transform results to match FE expectations
            products = []
            for item in result.get('results', []):
                product_data = item.get('product_data', {})
                # Add hybrid scores as metadata
                product_data['hybrid_score'] = item.get('hybrid_score', 0)
                product_data['semantic_score'] = item.get('semantic_score', 0)
                product_data['keyword_score'] = item.get('keyword_score', 0)
                products.append(product_data)
            
            return jsonify({
                "query": query,
                "results": products,
                "search_type": "hybrid_semantic_keyword",
                "total_found": len(products),
                "semantic_weight": semantic_weight,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "error": "Recommendation system error",
                "details": rec_response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendation-health', methods=['GET'])
def check_recommendation_system_health():
    """Check if the Recommendation System is available"""
    try:
        response = requests.get(f"{RECOMMENDATION_API_URL}/health", timeout=2.0)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "recommendation_system_available": True,
                "recommendation_system_status": data,
                "connection_url": RECOMMENDATION_API_URL
            })
        else:
            return jsonify({
                "recommendation_system_available": False,
                "error": f"HTTP {response.status_code}",
                "connection_url": RECOMMENDATION_API_URL
            })
            
    except Exception as e:
        return jsonify({
            "recommendation_system_available": False,
            "error": str(e),
            "connection_url": RECOMMENDATION_API_URL
        })

@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Process chatbot messages and return responses with product recommendations"""
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        
        # Simple chatbot logic for demonstration
        # In a real implementation, this would use NLP/AI services
        response_text = "Hello! I'm here to help you find products. What are you looking for?"
        products = []
        search_params = {}
        page_code = "others"
        
        # Basic product search logic
        if any(keyword in message for keyword in ["laptop", "computer", "pc"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if 'laptop' in p.get('name', '').lower() or 'computer' in p.get('name', '').lower()]
            search_params = {"category": "Electronics", "keywords": "laptop"}
            response_text = "I found some laptops for you!"
            page_code = "products"
        elif any(keyword in message for keyword in ["phone", "smartphone", "mobile"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if 'phone' in p.get('name', '').lower() or 'smartphone' in p.get('name', '').lower()]
            search_params = {"category": "Electronics", "keywords": "phone"}
            response_text = "Here are some smartphones I found!"
            page_code = "products"
        elif any(keyword in message for keyword in ["headphones", "headset", "earphones"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if any(word in p.get('name', '').lower() for word in ['headphone', 'headset', 'earphone'])]
            search_params = {"category": "Electronics", "keywords": "headphones"}
            response_text = "Check out these headphones!"
            page_code = "products"
        elif any(keyword in message for keyword in ["help", "hello", "hi"]):
            response_text = "Hello! I can help you find laptops, phones, headphones, and other electronics. What are you looking for?"
        
        return jsonify({
            "response": response_text,
            "products": products[:5],  # Limit to 5 products
            "search_params": search_params,
            "page_code": page_code
        })
        
    except Exception as e:
        print(f"Error processing chatbot request: {str(e)}")
        return jsonify({
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "products": [],
            "search_params": {},
            "page_code": "others"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting eCommerce Backend API Server (Flask)...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(host='127.0.0.1', port=8000, debug=True)
