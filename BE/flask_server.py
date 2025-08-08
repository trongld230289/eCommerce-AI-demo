from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
from firebase_config import get_firestore_db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Firebase Firestore helper functions
def get_all_products_from_firestore():
    """Get all products from Firebase Firestore"""
    try:
        db = get_firestore_db()
        if db is None:
            return []
        
        products_ref = db.collection('products')
        docs = products_ref.get()
        
        products = []
        for doc in docs:
            product = doc.to_dict()
            # Ensure ID is set properly
            product['id'] = int(doc.id)
            products.append(product)
        
        return products
    except Exception as e:
        print(f"Error fetching products from Firestore: {e}")
        return []

def get_product_by_id_from_firestore(product_id):
    """Get a specific product by ID from Firebase Firestore"""
    try:
        db = get_firestore_db()
        if db is None:
            return None
        
        doc_ref = db.collection('products').document(str(product_id))
        doc = doc_ref.get()
        
        if doc.exists:
            product = doc.to_dict()
            product['id'] = int(doc.id)
            return product
        return None
    except Exception as e:
        print(f"Error fetching product {product_id} from Firestore: {e}")
        return None

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
    """Search products - enhanced search can be implemented later"""
    try:
        products = get_all_products_from_firestore()
        return jsonify(products)
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
            
            popularity_score = sales_score + views_score
            
            product_copy = product.copy()
            product_copy['popularityScore'] = round(popularity_score, 3)
            product_copy['weekPeriod'] = f"{(datetime.now() - timedelta(days=7)).strftime('%m/%d')} - {datetime.now().strftime('%m/%d')}"
            products_with_score.append(product_copy)
        
        # Sort by popularity score
        products_with_score.sort(key=lambda x: x['popularityScore'], reverse=True)
        
        return jsonify(products_with_score[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized product recommendations from Firestore"""
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 4, type=int)
        
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
            product['recommendationReason'] = "Based on your preferences"
            product['recommendationScore'] = round(random.uniform(0.7, 0.95), 2)
        
        return jsonify(recommendations[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting eCommerce Backend API Server (Flask)...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(host='127.0.0.1', port=8000, debug=True)
