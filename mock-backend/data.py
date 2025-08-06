from models import Product

# Product data matching frontend format
products_data = [
    Product(
        id=1,
        name="Wireless Headphones",
        price=99.99,
        originalPrice=129.99,
        image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        category="Electronics",
        description="High-quality wireless headphones with noise cancellation",
        brand="AudioTech",
        tags=["wireless", "bluetooth", "noise-cancellation", "music"],
        color="Black",
        rating=4.5,
        isNew=True,
        discount=30
    ),
    Product(
        id=2,
        name="Smart Watch",
        price=299.99,
        originalPrice=349.99,
        image="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        category="Electronics",
        description="Advanced smartwatch with health monitoring and GPS",
        brand="TechWatch",
        tags=["smartwatch", "fitness", "health", "gps", "waterproof"],
        color="Silver",
        rating=4.7,
        discount=50
    ),
    Product(
        id=3,
        name="Gaming Laptop",
        price=999.99,
        originalPrice=1199.99,
        image="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
        category="Electronics",
        description="High-performance laptop for work and gaming with RTX graphics",
        brand="GameMaster",
        tags=["laptop", "gaming", "rtx", "high-performance", "work"],
        color="Black",
        rating=4.8,
        discount=200
    ),
    Product(
        id=4,
        name="Smartphone Pro",
        price=699.99,
        originalPrice=799.99,
        image="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
        category="Electronics",
        description="Latest smartphone with amazing camera and 5G connectivity",
        brand="PhoneTech",
        tags=["smartphone", "phone", "mobile", "camera", "5g", "photography"],
        color="Blue",
        rating=4.6,
        discount=100
    ),
    Product(
        id=5,
        name="Portable Bluetooth Speaker",
        price=79.99,
        originalPrice=99.99,
        image="https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500",
        category="Electronics",
        description="Portable bluetooth speaker with great sound and long battery life",
        brand="SoundWave",
        tags=["speaker", "bluetooth", "portable", "bass", "waterproof"],
        color="Red",
        rating=4.3,
        discount=20
    ),
    Product(
        id=6,
        name="RGB Gaming Mouse",
        price=49.99,
        originalPrice=69.99,
        image="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        category="Electronics",
        description="Professional gaming mouse with RGB lighting and precision sensor",
        brand="GamerGear",
        tags=["mouse", "gaming", "rgb", "precision", "esports"],
        color="Black",
        rating=4.4,
        discount=20
    ),
    Product(
        id=7,
        name="Mechanical Gaming Keyboard",
        price=129.99,
        originalPrice=159.99,
        image="https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500",
        category="Electronics",
        description="Mechanical keyboard for gaming and typing with RGB backlight",
        brand="KeyMaster",
        tags=["keyboard", "mechanical", "gaming", "rgb", "typing"],
        color="Black",
        rating=4.7,
        discount=30
    ),
    Product(
        id=8,
        name="iPad Tablet",
        price=399.99,
        originalPrice=449.99,
        image="https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500",
        category="Electronics",
        description="Lightweight tablet for work and entertainment with stylus support",
        brand="TabletPro",
        tags=["tablet", "stylus", "drawing", "work", "entertainment"],
        color="White",
        rating=4.5,
        discount=50
    )
]

# User preferences for personalized recommendations
user_preferences = {
    "user123": {
        "preferred_categories": ["Electronics"],
        "preferred_brands": ["AudioTech", "TechWatch"],
        "price_range": {"min": 50, "max": 300}
    },
    "user456": {
        "preferred_categories": ["Electronics"],
        "preferred_brands": ["GameMaster", "PhoneTech"],
        "price_range": {"min": 100, "max": 1000}
    }
}

# Curated recommendations for specific users
user_recommendations = {
    "user123": [1, 2, 5],  # Headphones, Smart Watch, Speaker
    "user456": [3, 4, 6]   # Gaming Laptop, Smartphone, Gaming Mouse
}

# Default recommendations for anonymous users
default_recommendations = [1, 2, 3, 4]

# Category-based cross-selling recommendations
category_recommendations = {
    "Electronics": [1, 2, 5, 6]
}
