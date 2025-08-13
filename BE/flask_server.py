from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import random
import requests
from datetime import datetime
from google.api_core.retry import Retry
from firebase_config import get_firestore_db

app = Flask(__name__)
CORS(app, methods=['GET', 'POST', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type'])

# Additional CORS handling for preflight requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ---------------------- Config ----------------------
RECOMMENDATION_API_URL = os.getenv("RECOMMENDATION_API_URL", "http://localhost:8001")
USE_FIREBASE = True  # Enable Firebase to read existing wishlist data

# Optional: avoid gRPC flakiness on Windows (set env outside too)
os.environ.setdefault("FIRESTORE_USE_GRPC", "false")

# Firestore retry/timeout settings
RETRY = Retry(initial=0.2, maximum=2.0, multiplier=2.0, deadline=5.0)
RPC_TIMEOUT = 3.0


# ---------------------- Firestore access ----------------------

def load_products_from_json():
    """Load products from products.json file"""
    try:
        products_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'products.json')
        if os.path.exists(products_file):
            with open(products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                print(f"Loaded {len(products)} products from products.json")
                return products
        else:
            print("products.json file not found")
            return get_sample_products()
    except Exception as e:
        print(f"Error loading products from JSON: {e}")
        return get_sample_products()

def get_all_products_from_firestore(limit: int = 200):
    """Read products with retry + timeout; fall back to JSON then sample data."""
    if not USE_FIREBASE:
        # Try loading from products.json first, then fall back to sample data
        products = load_products_from_json()
        return products[:limit] if len(products) > limit else products

    try:
        db = get_firestore_db()
        if db is None:
            return load_products_from_json()

        print("Attempting to fetch products from Firestore…")
        q = db.collection("products").order_by("id").limit(limit)
        docs = q.stream(retry=RETRY, timeout=RPC_TIMEOUT)

        products = []
        for d in docs:
            p = d.to_dict() or {}
            # Prefer stored numeric id; otherwise use doc id (string)
            p["id"] = p.get("id", d.id)
            products.append(p)

        if not products:
            print("No products found in Firestore, loading from JSON")
            return load_products_from_json()
        print(f"Fetched {len(products)} products from Firestore")
        return products
    except Exception as e:
        print(f"Error fetching products from Firestore: {e}")
        return load_products_from_json()


def get_product_by_id_from_firestore(product_id):
    if not USE_FIREBASE:
        # Try loading from products.json first
        products = load_products_from_json()
        return next((p for p in products if str(p["id"]) == str(product_id)), None)

    try:
        db = get_firestore_db()
        if db is None:
            products = load_products_from_json()
            return next((p for p in products if str(p["id"]) == str(product_id)), None)

        doc = db.collection("products").document(str(product_id)).get(timeout=RPC_TIMEOUT)
        if doc.exists:
            p = doc.to_dict() or {}
            p["id"] = p.get("id", doc.id)
            return p
        return None
    except Exception as e:
        print(f"Error fetching product {product_id} from Firestore: {e}")
        products = load_products_from_json()
        return next((p for p in products if str(p["id"]) == str(product_id)), None)

# ---------------------- Recommendation calls ----------------------

def send_user_event_to_recommendation_system(user_id, event_type, product_data):
    try:
        if not user_id or not event_type or not product_data:
            return False
        event_data = {
            "user_id": str(user_id),
            "event_type": event_type,
            "product_id": str(product_data.get("id", "")),
            "product_data": {
                "name": product_data.get("name", ""),
                "category": product_data.get("category", ""),
                "brand": product_data.get("brand", ""),
                "price": product_data.get("price", 0),
            },
            "metadata": {"timestamp": datetime.now().isoformat(), "source": "backend_api"},
        }
        r = requests.post(f"{RECOMMENDATION_API_URL}/user-events", json=event_data, timeout=2.0)
        if r.status_code == 201:
            print(f"✅ Event {event_type} sent to recommendation system for user {user_id}")
            return True
        print(f"❌ Failed to send event to recommendation system: {r.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error sending event to recommendation system: {e}")
        return False


def get_user_recommendations_from_system(user_id, limit=5):
    try:
        r = requests.get(f"{RECOMMENDATION_API_URL}/recommendations/{user_id}", params={"limit": limit}, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            return data.get("recommendations", [])
        print(f"❌ Failed to get recommendations: {r.status_code}")
        return []
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        return []


def smart_search_from_recommendation_system(query, limit=10):
    try:
        r = requests.post(f"{RECOMMENDATION_API_URL}/search", json={"query": query, "limit": limit}, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            return {
                "results": data.get("results", []),
                "parsed_filters": data.get("parsed_filters", {}),
                "total_found": data.get("total_found", 0),
            }
        print(f"❌ Failed to perform smart search: {r.status_code}")
        return {"results": [], "parsed_filters": {}, "total_found": 0}
    except Exception as e:
        print(f"❌ Error performing smart search: {e}")
        return {"results": [], "parsed_filters": {}, "total_found": 0}

# ---------------------- Routes ----------------------

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})


@app.route("/products", methods=["GET"])
def get_products():
    try:
        products = get_all_products_from_firestore()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/products/featured", methods=["GET"])
def get_featured_products():
    try:
        limit = request.args.get("limit", 6, type=int)
        products = get_all_products_from_firestore()
        featured_products = [p for p in products if p.get("featured", False)]
        featured_products.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return jsonify(featured_products[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/products/top-this-week", methods=["GET"])
def get_top_products_this_week():
    try:
        limit = request.args.get("limit", 6, type=int)
        products = get_all_products_from_firestore()

        max_sales = max((p.get("weeklySales", 0) for p in products), default=0)
        max_views = max((p.get("weeklyViews", 0) for p in products), default=0)

        scored = []
        for p in products:
            sales_score = (p.get("weeklySales", 0) / max_sales * 0.7) if max_sales else 0
            views_score = (p.get("weeklyViews", 0) / max_views * 0.3) if max_views else 0
            scored.append((p, sales_score + views_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_products = [p for p, _ in scored[:limit]]
        return jsonify(top_products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = get_product_by_id_from_firestore(product_id)
        if product:
            return jsonify(product)
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search", methods=["GET"])
def search_products():
    try:
        query = request.args.get("q", "").strip()
        limit = request.args.get("limit", 20, type=int)
        if query:
            sr = smart_search_from_recommendation_system(query, limit)
            return jsonify({
                "query": query,
                "results": sr["results"],
                "parsed_filters": sr["parsed_filters"],
                "total_found": sr["total_found"],
                "search_type": "smart_search",
            })
        products = get_all_products_from_firestore()
        return jsonify({
            "query": "",
            "results": products[:limit],
            "total_found": len(products),
            "search_type": "all_products",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/categories", methods=["GET"])
def get_categories():
    try:
        products = get_all_products_from_firestore()
        categories = sorted({p.get("category", "") for p in products if p.get("category")})
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/brands", methods=["GET"])
def get_brands():
    try:
        products = get_all_products_from_firestore()
        brands = sorted({p.get("brand", "") for p in products if p.get("brand")})
        return jsonify(brands)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- Recommendation (fallback route kept for compatibility) ----
@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    try:
        limit = request.args.get("limit", 4, type=int)
        user_id = request.args.get("user_id")

        if user_id:
            recs = get_user_recommendations_from_system(user_id, limit)
            if recs:
                for p in recs:
                    p["recommendationReason"] = "Based on your preferences"
                    p["recommendationScore"] = round(random.uniform(0.8, 0.95), 2)
                    p["source"] = "recommendation_system"
                return jsonify(recs[:limit])

        products = get_all_products_from_firestore()
        featured = [p for p in products if p.get("featured")]
        high_rated = [p for p in products if p.get("rating", 0) >= 4.5]

        recs = []
        if featured:
            recs.extend(random.sample(featured, min(2, len(featured))))
        remaining = limit - len(recs)
        if remaining > 0 and high_rated:
            pool = [p for p in high_rated if p not in recs]
            if pool:
                recs.extend(random.sample(pool, min(remaining, len(pool))))
        remaining = limit - len(recs)
        if remaining > 0:
            pool = [p for p in products if p not in recs]
            if pool:
                recs.extend(random.sample(pool, min(remaining, len(pool))))

        for p in recs:
            p["recommendationReason"] = "Popular products"
            p["recommendationScore"] = round(random.uniform(0.7, 0.85), 2)
            p["source"] = "fallback_algorithm"

        return jsonify(recs[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- Events ----------------------

def save_user_event_to_firestore(event_data):
    try:
        db = get_firestore_db()
        if db is None:
            print("Database connection failed for event tracking")
            return None
        event_data["timestamp"] = datetime.now()
        ref = db.collection("user_events").add(event_data, timeout=RPC_TIMEOUT)
        return ref[1].id
    except Exception as e:
        print(f"Error saving event to Firestore: {e}")
        return None


@app.route("/events", methods=["POST"])
def track_user_event():
    try:
        data = request.get_json()
        required_fields = ["event_type", "user_id", "product_id"]
        for f in required_fields:
            if f not in data:
                return jsonify({"error": f"Missing required field: {f}"}), 400

        valid_event_types = [
            "view",
            "add_to_cart",
            "remove_from_cart",
            "add_to_wishlist",
            "remove_from_wishlist",
        ]
        if data["event_type"] not in valid_event_types:
            return jsonify({"error": f"Invalid event_type. Must be one of: {valid_event_types}"}), 400

        product = get_product_by_id_from_firestore(data["product_id"]) if data.get("product_id") else None
        if "metadata" not in data or not data["metadata"]:
            if product:
                data["metadata"] = {
                    "product_name": product.get("name"),
                    "product_category": product.get("category"),
                    "product_brand": product.get("brand"),
                    "product_price": product.get("price"),
                    "device": "web",
                    "source": "unknown",
                }
            else:
                data["metadata"] = {"device": "web", "source": "unknown"}

        event_id = save_user_event_to_firestore(data)
        recommendation_success = False
        if product:
            recommendation_success = send_user_event_to_recommendation_system(
                data["user_id"], data["event_type"], product
            )

        if event_id:
            return jsonify(
                {
                    "success": True,
                    "message": "Event tracked successfully",
                    "event_id": event_id,
                    "firebase_saved": True,
                    "recommendation_system_sent": recommendation_success,
                }
            )
        return jsonify({"error": "Failed to save event"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/events/<user_id>", methods=["GET"])
def get_user_events(user_id):
    try:
        db = get_firestore_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500

        limit = request.args.get("limit", 100, type=int)
        event_type = request.args.get("event_type")

        q = db.collection("user_events").where("user_id", "==", user_id)
        if event_type:
            q = q.where("event_type", "==", event_type)
        q = q.order_by("timestamp", direction="DESCENDING").limit(limit)
        docs = q.get(timeout=RPC_TIMEOUT)

        events = []
        for d in docs:
            ev = d.to_dict()
            ev["id"] = d.id
            if ev.get("timestamp"):
                ev["timestamp"] = ev["timestamp"].isoformat()
            events.append(ev)
        return jsonify({"success": True, "events": events, "count": len(events)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/events/analytics/<user_id>", methods=["GET"])
def get_user_analytics(user_id):
    try:
        db = get_firestore_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        docs = db.collection("user_events").where("user_id", "==", user_id).get(timeout=RPC_TIMEOUT)

        analytics = {
            "total_events": 0,
            "events_by_type": {},
            "most_viewed_products": {},
            "most_viewed_categories": {},
            "cart_actions": 0,
            "wishlist_actions": 0,
        }
        for d in docs:
            e = d.to_dict()
            analytics["total_events"] += 1
            et = e.get("event_type", "unknown")
            analytics["events_by_type"][et] = analytics["events_by_type"].get(et, 0) + 1
            if et == "view":
                pid = e.get("product_id")
                analytics["most_viewed_products"][pid] = analytics["most_viewed_products"].get(pid, 0) + 1
                cat = (e.get("metadata") or {}).get("product_category")
                if cat:
                    analytics["most_viewed_categories"][cat] = analytics["most_viewed_categories"].get(cat, 0) + 1
            if et in ["add_to_cart", "remove_from_cart"]:
                analytics["cart_actions"] += 1
            if et in ["add_to_wishlist", "remove_from_wishlist"]:
                analytics["wishlist_actions"] += 1
        return jsonify({"success": True, "analytics": analytics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- Rec Sys Utilities ----------------------

@app.route("/recommendation-health", methods=["GET"])
def check_recommendation_system_health():
    try:
        r = requests.get(f"{RECOMMENDATION_API_URL}/health", timeout=2.0)
        if r.status_code == 200:
            return jsonify({
                "recommendation_system_available": True,
                "recommendation_system_status": r.json(),
                "connection_url": RECOMMENDATION_API_URL,
            })
        return jsonify({
            "recommendation_system_available": False,
            "error": f"HTTP {r.status_code}",
            "connection_url": RECOMMENDATION_API_URL,
        })
    except Exception as e:
        return jsonify({"recommendation_system_available": False, "error": str(e), "connection_url": RECOMMENDATION_API_URL})


# ---------------------- Simple Chatbot Demo ----------------------

@app.route("/chatbot", methods=["POST"])
def chatbot_endpoint():
    try:
        data = request.get_json() or {}
        message = (data.get("message") or "").lower()

        response_text = "Hello! I'm here to help you find products. What are you looking for?"
        products = []
        search_params = {}
        page_code = "others"

        if any(k in message for k in ["laptop", "computer", "pc"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if any(w in (p.get("name", "").lower()) for w in ["laptop", "computer"])]
            search_params = {"category": "Electronics", "keywords": "laptop"}
            response_text = "I found some laptops for you!"
            page_code = "products"
        elif any(k in message for k in ["phone", "smartphone", "mobile"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if any(w in (p.get("name", "").lower()) for w in ["phone", "smartphone"])]
            search_params = {"category": "Electronics", "keywords": "phone"}
            response_text = "Here are some smartphones I found!"
            page_code = "products"
        elif any(k in message for k in ["headphones", "headset", "earphones"]):
            all_products = get_all_products_from_firestore()
            products = [p for p in all_products if any(w in (p.get("name", "").lower()) for w in ["headphone", "headset", "earphone"])]
            search_params = {"category": "Electronics", "keywords": "headphones"}
            response_text = "Check out these headphones!"
            page_code = "products"
        elif any(k in message for k in ["help", "hello", "hi"]):
            response_text = "Hello! I can help you find laptops, phones, headphones, and other electronics. What are you looking for?"

        return jsonify({
            "response": response_text,
            "products": products[:5],
            "search_params": search_params,
            "page_code": page_code,
        })
    except Exception as e:
        print(f"Error processing chatbot request: {str(e)}")
        return jsonify({
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "products": [],
            "search_params": {},
            "page_code": "others",
        }), 500


# ---------------------- Wishlist Management ----------------------

# In-memory storage for demo purposes (replace with database in production)
demo_wishlists = []
demo_wishlist_counter = 1

def enhance_wishlist_with_product_details(wishlist):
    """Enhance wishlist products with full product details"""
    if not wishlist or "products" not in wishlist:
        return wishlist
    
    print(f"Debug: Enhancing wishlist {wishlist.get('id')} with {len(wishlist['products'])} products")
    enhanced_products = []
    for item in wishlist["products"]:
        if isinstance(item, dict) and "product_id" in item:
            # Get full product details
            product = get_product_by_id_from_firestore(item["product_id"])
            print(f"Debug: Product {item['product_id']} found: {product is not None}")
            if product:
                # Create enhanced product object with wishlist metadata
                enhanced_item = {
                    "product_id": item["product_id"],
                    "added_at": item.get("added_at"),
                    "product": product  # Full product details
                }
                enhanced_products.append(enhanced_item)
                print(f"Debug: Enhanced item keys: {list(enhanced_item.keys())}")
            else:
                # Keep original if product not found
                enhanced_products.append(item)
        else:
            # Keep original if not a proper wishlist item
            enhanced_products.append(item)
    
    # Update wishlist with enhanced products
    enhanced_wishlist = wishlist.copy()
    enhanced_wishlist["products"] = enhanced_products
    print(f"Debug: Enhanced wishlist product count: {len(enhanced_products)}")
    return enhanced_wishlist

def get_user_wishlists_from_firestore(user_id):
    """Get all wishlists for a user - Demo version using in-memory storage"""
    try:
        if USE_FIREBASE:
            db = get_firestore_db()
            if db is None:
                wishlists = [wishlist for wishlist in demo_wishlists if wishlist.get("user_id") == user_id]
                return [enhance_wishlist_with_product_details(w) for w in wishlists]

            docs = db.collection("wishlists").where("user_id", "==", user_id).get(timeout=RPC_TIMEOUT)
            wishlists = []
            for doc in docs:
                wishlist = doc.to_dict()
                wishlist["id"] = doc.id
                # Ensure products is a list and count items
                products = wishlist.get("products", [])
                if not isinstance(products, list):
                    products = []
                wishlist["products"] = products
                wishlist["item_count"] = len(products)
                wishlists.append(enhance_wishlist_with_product_details(wishlist))
            
            return wishlists
        else:
            # Demo mode: use in-memory storage
            wishlists = [wishlist for wishlist in demo_wishlists if wishlist.get("user_id") == user_id]
            return [enhance_wishlist_with_product_details(w) for w in wishlists]
    except Exception as e:
        print(f"Error fetching wishlists: {e}")
        # Fallback to demo storage
        wishlists = [wishlist for wishlist in demo_wishlists if wishlist.get("user_id") == user_id]
        return [enhance_wishlist_with_product_details(w) for w in wishlists]


def create_wishlist_in_firestore(user_id, name):
    """Create a new wishlist - Demo version using in-memory storage"""
    global demo_wishlist_counter
    
    try:
        if USE_FIREBASE:
            db = get_firestore_db()
            if db is None:
                # Fallback to demo storage
                wishlist_data = {
                    "id": str(demo_wishlist_counter),
                    "user_id": user_id,
                    "name": name,
                    "products": [],
                    "item_count": 0,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                demo_wishlists.append(wishlist_data)
                demo_wishlist_counter += 1
                return wishlist_data

            wishlist_data = {
                "user_id": user_id,
                "name": name,
                "products": [],
                "item_count": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            doc_ref = db.collection("wishlists").add(wishlist_data, timeout=RPC_TIMEOUT)
            wishlist_data["id"] = doc_ref[1].id
            return wishlist_data
        else:
            # Demo mode: use in-memory storage
            wishlist_data = {
                "id": str(demo_wishlist_counter),
                "user_id": user_id,
                "name": name,
                "products": [],
                "item_count": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            demo_wishlists.append(wishlist_data)
            demo_wishlist_counter += 1
            return wishlist_data
    except Exception as e:
        print(f"Error creating wishlist: {e}")
        # Fallback to demo storage
        wishlist_data = {
            "id": str(demo_wishlist_counter),
            "user_id": user_id,
            "name": name,
            "products": [],
            "item_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        demo_wishlists.append(wishlist_data)
        demo_wishlist_counter += 1
        return wishlist_data


def add_product_to_wishlist_in_firestore(wishlist_id, user_id, product_id):
    """Add a product to wishlist - Demo version using in-memory storage"""
    try:
        if USE_FIREBASE:
            db = get_firestore_db()
            if db is None:
                # Fallback to demo storage
                for wishlist in demo_wishlists:
                    if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                        # Check if product already exists
                        for item in wishlist["products"]:
                            if item.get("product_id") == product_id:
                                raise Exception("Product already in wishlist")
                        
                        # Add new product
                        wishlist["products"].append({
                            "product_id": product_id,
                            "added_at": datetime.now().timestamp()
                        })
                        wishlist["item_count"] = len(wishlist["products"])
                        wishlist["updated_at"] = datetime.now().isoformat()
                        return enhance_wishlist_with_product_details(wishlist)
                return None

            # Verify product exists
            product = get_product_by_id_from_firestore(product_id)
            if not product:
                raise Exception("Product not found")

            doc_ref = db.collection("wishlists").document(wishlist_id)
            doc = doc_ref.get(timeout=RPC_TIMEOUT)
            
            if not doc.exists:
                return None
            
            wishlist = doc.to_dict()
            if wishlist.get("user_id") != user_id:
                return None
            
            products = wishlist.get("products", [])
            if not isinstance(products, list):
                products = []
            
            # Check if product already exists
            for item in products:
                if item.get("product_id") == product_id:
                    raise Exception("Product already in wishlist")
            
            # Add new product
            products.append({
                "product_id": product_id,
                "added_at": datetime.now().timestamp()
            })
            
            # Update wishlist
            update_data = {
                "products": products,
                "item_count": len(products),
                "updated_at": datetime.now()
            }
            
            doc_ref.update(update_data, timeout=RPC_TIMEOUT)
            
            # Return updated wishlist with product details
            wishlist.update(update_data)
            wishlist["id"] = wishlist_id
            return enhance_wishlist_with_product_details(wishlist)
        else:
            # Demo mode: use in-memory storage
            for wishlist in demo_wishlists:
                if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                    # Check if product already exists
                    for item in wishlist["products"]:
                        if item.get("product_id") == product_id:
                            raise Exception("Product already in wishlist")
                    
                    # Add new product
                    wishlist["products"].append({
                        "product_id": product_id,
                        "added_at": datetime.now().timestamp()
                    })
                    wishlist["item_count"] = len(wishlist["products"])
                    wishlist["updated_at"] = datetime.now().isoformat()
                    return enhance_wishlist_with_product_details(wishlist)
            return None
    except Exception as e:
        print(f"Error adding product to wishlist: {e}")
        # Fallback to demo storage if Firebase fails
        if "Product already in wishlist" in str(e):
            raise  # Re-raise this specific error
        for wishlist in demo_wishlists:
            if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                # Check if product already exists
                for item in wishlist["products"]:
                    if item.get("product_id") == product_id:
                        raise Exception("Product already in wishlist")
                
                # Add new product
                wishlist["products"].append({
                    "product_id": product_id,
                    "added_at": datetime.now().timestamp()
                })
                wishlist["item_count"] = len(wishlist["products"])
                wishlist["updated_at"] = datetime.now().isoformat()
                return enhance_wishlist_with_product_details(wishlist)
        return None


def remove_product_from_wishlist_in_firestore(wishlist_id, user_id, product_id):
    """Remove a product from wishlist - Demo version using in-memory storage"""
    try:
        if USE_FIREBASE:
            db = get_firestore_db()
            if db is None:
                # Fallback to demo storage
                for wishlist in demo_wishlists:
                    if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                        # Remove product
                        wishlist["products"] = [item for item in wishlist["products"] if item.get("product_id") != product_id]
                        wishlist["item_count"] = len(wishlist["products"])
                        wishlist["updated_at"] = datetime.now().isoformat()
                        return enhance_wishlist_with_product_details(wishlist)
                return None

            doc_ref = db.collection("wishlists").document(wishlist_id)
            doc = doc_ref.get(timeout=RPC_TIMEOUT)
            
            if not doc.exists:
                return None
            
            wishlist = doc.to_dict()
            if wishlist.get("user_id") != user_id:
                return None
            
            products = wishlist.get("products", [])
            if not isinstance(products, list):
                products = []
            
            # Remove product
            products = [item for item in products if item.get("product_id") != product_id]
            
            # Update wishlist
            update_data = {
                "products": products,
                "item_count": len(products),
                "updated_at": datetime.now()
            }
            
            doc_ref.update(update_data, timeout=RPC_TIMEOUT)
            
            # Return updated wishlist with product details
            wishlist.update(update_data)
            wishlist["id"] = wishlist_id
            return enhance_wishlist_with_product_details(wishlist)
        else:
            # Demo mode: use in-memory storage
            for wishlist in demo_wishlists:
                if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                    # Remove product
                    wishlist["products"] = [item for item in wishlist["products"] if item.get("product_id") != product_id]
                    wishlist["item_count"] = len(wishlist["products"])
                    wishlist["updated_at"] = datetime.now().isoformat()
                    return enhance_wishlist_with_product_details(wishlist)
            return None
    except Exception as e:
        print(f"Error removing product from wishlist: {e}")
        # Fallback to demo storage
        for wishlist in demo_wishlists:
            if wishlist["id"] == wishlist_id and wishlist["user_id"] == user_id:
                # Remove product
                wishlist["products"] = [item for item in wishlist["products"] if item.get("product_id") != product_id]
                wishlist["item_count"] = len(wishlist["products"])
                wishlist["updated_at"] = datetime.now().isoformat()
                return enhance_wishlist_with_product_details(wishlist)
        return None


@app.route("/api/test", methods=["POST"])
def test_post():
    """Test POST endpoint"""
    print("DEBUG: Test POST endpoint hit!")
    return jsonify({"message": "POST test successful"})


@app.route("/api/wishlist", methods=["GET"])
def get_user_wishlists():
    """Get all wishlists for a user"""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        wishlists = get_user_wishlists_from_firestore(user_id)
        print(f"Debug: API returning {len(wishlists)} wishlists for user {user_id}")
        if wishlists:
            print(f"Debug: First wishlist product keys: {list(wishlists[0]['products'][0].keys()) if wishlists[0].get('products') else 'No products'}")
        return jsonify(wishlists)
    except Exception as e:
        print(f"Error in get_user_wishlists: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wishlist", methods=["POST"])
def create_wishlist():
    """Create a new wishlist"""
    print("DEBUG: Create wishlist endpoint hit!")
    try:
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")
        if not data or not data.get("name"):
            print("DEBUG: Missing name in request")
            return jsonify({"error": "Wishlist name is required"}), 400
        
        user_id = data.get("user_id")
        if not user_id:
            print("DEBUG: Missing user_id in request")
            return jsonify({"error": "user_id is required"}), 400
        
        print(f"DEBUG: Creating wishlist for user {user_id} with name {data['name']}")
        wishlist = create_wishlist_in_firestore(user_id, data["name"])
        if not wishlist:
            print("DEBUG: Failed to create wishlist")
            return jsonify({"error": "Failed to create wishlist"}), 500
        
        print(f"DEBUG: Created wishlist: {wishlist}")
        return jsonify(wishlist)
    except Exception as e:
        print(f"DEBUG: Exception in create_wishlist: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wishlist/<wishlist_id>/products", methods=["POST"])
def add_product_to_wishlist(wishlist_id):
    """Add a product to wishlist"""
    try:
        data = request.get_json()
        if not data or not data.get("product_id"):
            return jsonify({"error": "Product ID is required"}), 400
        
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        product_id = int(data["product_id"])
        wishlist = add_product_to_wishlist_in_firestore(wishlist_id, user_id, product_id)
        
        if not wishlist:
            return jsonify({"error": "Wishlist not found"}), 404
        
        return jsonify(wishlist)
    except ValueError:
        return jsonify({"error": "Invalid product ID"}), 400
    except Exception as e:
        if "already in wishlist" in str(e):
            return jsonify({"error": str(e)}), 400
        if "Product not found" in str(e):
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500


@app.route("/api/wishlist/<wishlist_id>/products/<int:product_id>", methods=["DELETE"])
def remove_product_from_wishlist(wishlist_id, product_id):
    """Remove a product from wishlist"""
    try:
        print(f"[DEBUG] DELETE request to remove product {product_id} from wishlist {wishlist_id}")
        user_id = request.args.get("user_id")
        print(f"[DEBUG] Received user_id: {user_id}")
        if not user_id:
            print("[DEBUG] Error: user_id parameter is missing")
            return jsonify({"error": "user_id parameter is required"}), 400
        
        wishlist = remove_product_from_wishlist_in_firestore(wishlist_id, user_id, product_id)
        
        if not wishlist:
            print(f"[DEBUG] Error: Wishlist {wishlist_id} not found for user {user_id}")
            return jsonify({"error": "Wishlist not found"}), 404
        
        print(f"[DEBUG] Successfully removed product {product_id} from wishlist {wishlist_id}")
        return jsonify(wishlist)
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wishlist/<wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """Delete a wishlist"""
    try:
        print(f"[DEBUG] DELETE request to delete wishlist {wishlist_id}")
        user_id = request.args.get("user_id")
        print(f"[DEBUG] Received user_id: {user_id}")
        if not user_id:
            print("[DEBUG] Error: user_id parameter is missing")
            return jsonify({"error": "user_id parameter is required"}), 400
        
        # Delete wishlist from Firestore
        success = delete_wishlist_from_firestore(wishlist_id, user_id)
        
        if not success:
            print(f"[DEBUG] Error: Wishlist {wishlist_id} not found for user {user_id}")
            return jsonify({"error": "Wishlist not found or not authorized"}), 404
        
        print(f"[DEBUG] Successfully deleted wishlist {wishlist_id}")
        return jsonify({"message": "Wishlist deleted successfully"}), 200
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wishlist/<wishlist_id>/debug", methods=["GET"])
def debug_wishlist_route(wishlist_id):
    """Debug route to test if routing is working"""
    return jsonify({"message": f"Debug route working for wishlist_id: {wishlist_id}"}), 200


def delete_wishlist_from_firestore(wishlist_id, user_id):
    """Delete a wishlist from Firestore"""
    global demo_wishlists
    try:
        if USE_FIREBASE:
            db = get_firestore_db()
            if db is None:
                # Fallback to demo storage
                demo_wishlists = [w for w in demo_wishlists if not (w["id"] == wishlist_id and w["user_id"] == user_id)]
                return True

            # Get the wishlist first to verify ownership
            wishlist_ref = db.collection("wishlists").document(wishlist_id)
            wishlist_doc = wishlist_ref.get(timeout=RPC_TIMEOUT)
            
            if not wishlist_doc.exists:
                return False
                
            wishlist_data = wishlist_doc.to_dict()
            if wishlist_data.get("user_id") != user_id:
                return False
                
            # Delete the wishlist
            wishlist_ref.delete()
            return True
        else:
            # Demo mode - remove from in-memory storage
            original_count = len(demo_wishlists)
            demo_wishlists = [w for w in demo_wishlists if not (w["id"] == wishlist_id and w["user_id"] == user_id)]
            return len(demo_wishlists) < original_count
        
    except Exception as e:
        print(f"Error deleting wishlist from Firestore: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting eCommerce Backend API Server (Flask)…")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # List all registered routes for debugging
    print("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})")
    print("-" * 50)
    
    # Avoid double init of Firebase in debug
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
