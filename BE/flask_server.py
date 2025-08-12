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
CORS(app)

# ---------------------- Config ----------------------
RECOMMENDATION_API_URL = os.getenv("RECOMMENDATION_API_URL", "http://localhost:8001")
USE_FIREBASE = os.getenv("USE_FIREBASE", "true").lower() == "true"

# Optional: avoid gRPC flakiness on Windows (set env outside too)
os.environ.setdefault("FIRESTORE_USE_GRPC", "false")

# Firestore retry/timeout settings
RETRY = Retry(initial=0.2, maximum=2.0, multiplier=2.0, deadline=5.0)
RPC_TIMEOUT = 3.0

# ---------------------- Helpers ----------------------

def get_sample_products():
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
            "weeklyViews": 1250,
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
            "weeklyViews": 890,
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
            "weeklyViews": 1580,
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
            "weeklyViews": 720,
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
            "weeklyViews": 1120,
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
            "weeklyViews": 950,
        },
    ]

# ---------------------- Firestore access ----------------------

def get_all_products_from_firestore(limit: int = 200):
    """Read products with retry + timeout; fall back to sample data."""
    if not USE_FIREBASE:
        return get_sample_products()

    try:
        db = get_firestore_db()
        if db is None:
            return get_sample_products()

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
            print("No products found in Firestore, using sample data")
            return get_sample_products()
        print(f"Fetched {len(products)} products from Firestore")
        return products
    except Exception as e:
        print(f"Error fetching products from Firestore: {e}")
        return get_sample_products()


def get_product_by_id_from_firestore(product_id):
    if not USE_FIREBASE:
        return next((p for p in get_sample_products() if str(p["id"]) == str(product_id)), None)

    try:
        db = get_firestore_db()
        if db is None:
            return next((p for p in get_sample_products() if str(p["id"]) == str(product_id)), None)

        doc = db.collection("products").document(str(product_id)).get(timeout=RPC_TIMEOUT)
        if doc.exists:
            p = doc.to_dict() or {}
            p["id"] = p.get("id", doc.id)
            return p
        return None
    except Exception as e:
        print(f"Error fetching product {product_id} from Firestore: {e}")
        return next((p for p in get_sample_products() if str(p["id"]) == str(product_id)), None)

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

@app.get("/health")
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})


@app.get("/products")
def get_products():
    try:
        products = get_all_products_from_firestore()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/products/featured")
def get_featured_products():
    try:
        limit = request.args.get("limit", 6, type=int)
        products = get_all_products_from_firestore()
        featured_products = [p for p in products if p.get("featured", False)]
        featured_products.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return jsonify(featured_products[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/products/top-this-week")
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


@app.get("/products/<int:product_id>")
def get_product(product_id):
    try:
        product = get_product_by_id_from_firestore(product_id)
        if product:
            return jsonify(product)
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/search")
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


@app.get("/categories")
def get_categories():
    try:
        products = get_all_products_from_firestore()
        categories = sorted({p.get("category", "") for p in products if p.get("category")})
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/brands")
def get_brands():
    try:
        products = get_all_products_from_firestore()
        brands = sorted({p.get("brand", "") for p in products if p.get("brand")})
        return jsonify(brands)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- Recommendation (fallback route kept for compatibility) ----
@app.get("/recommendations")
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


@app.post("/events")
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


@app.get("/events/<user_id>")
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


@app.get("/events/analytics/<user_id>")
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

@app.get("/recommendation-health")
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

@app.post("/chatbot")
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


if __name__ == "__main__":
    print("🚀 Starting eCommerce Backend API Server (Flask)…")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    # Avoid double init of Firebase in debug
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
