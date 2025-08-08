from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock data
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 99.99,
        "category": "Electronics",
        "brand": "AudioTech",
        "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "stock": 50,
        "rating": 4.5,
        "featured": True,
        "weeklyViews": 1250,
        "weeklySales": 45
    },
    {
        "id": 2,
        "name": "Smart Fitness Watch",
        "description": "Track your fitness goals with this advanced smartwatch",
        "price": 299.99,
        "category": "Electronics",
        "brand": "FitTech",
        "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "stock": 30,
        "rating": 4.7,
        "featured": True,
        "weeklyViews": 980,
        "weeklySales": 32
    },
    {
        "id": 3,
        "name": "Portable Laptop Stand",
        "description": "Ergonomic adjustable laptop stand for better posture",
        "price": 49.99,
        "category": "Accessories",
        "brand": "ErgoDesk",
        "imageUrl": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        "stock": 75,
        "rating": 4.3,
        "featured": False,
        "weeklyViews": 650,
        "weeklySales": 28
    },
    {
        "id": 4,
        "name": "USB-C Hub",
        "description": "Multi-port USB-C hub with HDMI, USB-A, and SD card slots",
        "price": 79.99,
        "category": "Accessories",
        "brand": "TechConnect",
        "imageUrl": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500",
        "stock": 40,
        "rating": 4.4,
        "featured": True,
        "weeklyViews": 820,
        "weeklySales": 38
    },
    {
        "id": 5,
        "name": "Wireless Charging Pad",
        "description": "Fast wireless charging pad compatible with all Qi devices",
        "price": 34.99,
        "category": "Accessories",
        "brand": "PowerWave",
        "imageUrl": "https://images.unsplash.com/photo-1609592067784-e4a9d8f1b3d1?w=500",
        "stock": 60,
        "rating": 4.2,
        "featured": False,
        "weeklyViews": 450,
        "weeklySales": 22
    },
    {
        "id": 6,
        "name": "Gaming Mechanical Keyboard",
        "description": "RGB backlit mechanical keyboard for gaming enthusiasts",
        "price": 149.99,
        "category": "Gaming",
        "brand": "GameForce",
        "imageUrl": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500",
        "stock": 25,
        "rating": 4.8,
        "featured": True,
        "weeklyViews": 1100,
        "weeklySales": 42
    },
    {
        "id": 7,
        "name": "Noise-Cancelling Earbuds",
        "description": "Premium wireless earbuds with active noise cancellation",
        "price": 199.99,
        "category": "Electronics",
        "brand": "AudioTech",
        "imageUrl": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
        "stock": 35,
        "rating": 4.6,
        "featured": True,
        "weeklyViews": 1350,
        "weeklySales": 48
    },
    {
        "id": 8,
        "name": "Smart Home Security Camera",
        "description": "1080p HD security camera with night vision and mobile alerts",
        "price": 129.99,
        "category": "Smart Home",
        "brand": "SecureVision",
        "imageUrl": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
        "stock": 42,
        "rating": 4.4,
        "featured": False,
        "weeklyViews": 890,
        "weeklySales": 35
    }
]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(MOCK_PRODUCTS)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/search', methods=['GET'])
def search_products():
    # Simple search implementation
    return jsonify(MOCK_PRODUCTS)

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = list(set(p['category'] for p in MOCK_PRODUCTS))
    return jsonify(categories)

@app.route('/brands', methods=['GET'])
def get_brands():
    brands = list(set(p['brand'] for p in MOCK_PRODUCTS))
    return jsonify(brands)

@app.route('/products', methods=['GET'])
def get_all_products():
    """Get all products"""
    try:
        return jsonify(MOCK_PRODUCTS)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        limit = request.args.get('limit', 6, type=int)
        featured_products = [p for p in MOCK_PRODUCTS if p.get('featured', False)]
        # Sort by rating for best featured products first
        featured_products.sort(key=lambda x: x['rating'], reverse=True)
        return jsonify(featured_products[:limit])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/top-this-week', methods=['GET'])
def get_top_products_this_week():
    """Get Top Products This Week based on views and sales"""
    try:
        limit = request.args.get('limit', 6, type=int)
        
        # Calculate popularity score based on views and sales
        products_with_score = []
        for product in MOCK_PRODUCTS:
            # Weight: 70% weekly sales, 30% weekly views (normalized)
            max_sales = max(p.get('weeklySales', 0) for p in MOCK_PRODUCTS)
            max_views = max(p.get('weeklyViews', 0) for p in MOCK_PRODUCTS)
            
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
    """Get personalized product recommendations"""
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 4, type=int)
        
        # Simple recommendation algorithm: 
        # 1. Include some featured products
        # 2. Include some high-rated products
        # 3. Add some random variety
        
        featured_products = [p for p in MOCK_PRODUCTS if p.get('featured', False)]
        high_rated_products = [p for p in MOCK_PRODUCTS if p['rating'] >= 4.5]
        
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
            available_products = [p for p in MOCK_PRODUCTS if p not in recommendations]
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
