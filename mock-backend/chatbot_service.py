import json
import os
from typing import List, Optional, Dict, Any
from openai import AzureOpenAI
from data import products_data
from models import Product

# Initialize OpenAI client (you'll need to set OPENAI_API_KEY environment variable)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")

# Step 1: Set your Azure OpenAI API key with error handling
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
if not azure_endpoint or not api_key:
    raise ValueError(
        "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables"
    )
client = None
try:
    client = AzureOpenAI(
    api_version="2024-07-01-preview",
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    )
except Exception as e:
    print(f"Warning: OpenAI client not initialized. Set AZURE_OPENAI_API_KEY environment variable. Error: {e}")

def search_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    keywords: Optional[List[str]] = None
) -> List[Product]:
    """
    Search products based on filters
    """
    filtered_products = products_data.copy()
    
    # Filter by category
    if category:
        filtered_products = [p for p in filtered_products if category.lower() in p.category.lower()]
    
    # Filter by brand
    if brand:
        filtered_products = [p for p in filtered_products if p.brand and brand.lower() in p.brand.lower()]
    
    # Filter by price range
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    # Filter by keywords in name, description, and tags (but not brand to avoid confusion)
    if keywords:
        import re
        keyword_filtered = []
        for product in filtered_products:
            # Check if any keyword matches product name, description, or tags
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Use word boundaries to match whole words only
                # This prevents "phone" from matching "headphone"
                word_pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                
                # Check in product name
                name_match = re.search(word_pattern, product.name.lower())
                # Check in description
                desc_match = re.search(word_pattern, product.description.lower())
                # Check in tags
                tag_match = any(re.search(word_pattern, tag.lower()) for tag in product.tags)
                
                if name_match or desc_match or tag_match:
                    if product not in keyword_filtered:
                        keyword_filtered.append(product)
                    break  # Found a match, no need to check other keywords for this product
        filtered_products = keyword_filtered
    
    return filtered_products[:10]  # Limit to 10 results

# Function definitions for OpenAI (tools format)
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products based on category, brand, price range, and keywords",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category (e.g., 'Electronics')"
                    },
                    "brand": {
                        "type": "string", 
                        "description": "Product brand (e.g., 'AudioTech', 'TechWatch', 'GameMaster', 'PhoneTech', 'SoundWave', 'GamerGear', 'KeyMaster', 'TabletPro')"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price in USD"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search in product name, description, and tags. Extract main product types like 'phone', 'laptop', 'headphones', etc., not brand names."
                    }
                },
                "required": []
            }
        }
    }
]

def convert_price_to_usd(price_str: str) -> Optional[float]:
    """Convert price string with various formats to USD"""
    if not price_str:
        return None
    
    # Remove currency symbols and normalize
    price_str = price_str.replace('$', '').replace(',', '').replace(' ', '').lower()
    
    try:
        price = float(price_str)
        # Assume it's already in USD
        return price
    except ValueError:
        return None

async def process_chatbot_query(user_message: str) -> Dict[str, Any]:
    """
    Process user message using OpenAI function calling to extract product search parameters
    """
    if not client:
        # Fallback: simple keyword matching if OpenAI is not available
        return await fallback_product_search(user_message)
    
    try:
        # Create system prompt
        system_prompt = """You are a helpful e-commerce assistant. When users ask about products, use the search_products function to find relevant items. 
        
        Available categories: Electronics
        Available brands: AudioTech, TechWatch, GameMaster, PhoneTech, SoundWave, GamerGear, KeyMaster, TabletPro
        
        Extract category, brand, price range, and relevant keywords from user queries. Prices are in USD."""
        
        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=tools,  # type: ignore
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            # Extract function arguments from the first tool call
            tool_call = message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the search function
            products = search_products(
                category=function_args.get("category"),
                brand=function_args.get("brand"),
                min_price=function_args.get("min_price"),
                max_price=function_args.get("max_price"),
                keywords=function_args.get("keywords")
            )
            
            # Generate response message
            if products:
                product_list = "\n".join([
                    f"• {product.name} - {product.brand} - ${product.price:.2f}"
                    for product in products[:5]
                ])
                response_text = f"I found {len(products)} products matching your criteria:\n\n{product_list}"
                if len(products) > 5:
                    response_text += f"\n\n... and {len(products) - 5} more products."
            else:
                response_text = "I couldn't find any products matching your criteria. Try adjusting your search terms."
            
            return {
                "response": response_text,
                "products": [product.model_dump() for product in products],
                "search_params": function_args
            }
        else:
            # No function call, return regular response
            return {
                "response": message.content,
                "products": [],
                "search_params": {}
            }
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return await fallback_product_search(user_message)

async def fallback_product_search(user_message: str) -> Dict[str, Any]:
    """
    Fallback product search using simple keyword matching when OpenAI is not available
    """
    message_lower = user_message.lower()
    
    # Simple keyword extraction
    category = None
    brand = None
    keywords = []
    min_price = None
    max_price = None
    
    # Category mapping
    category_keywords = {
        "electronics": ["electronics", "electronic", "tech", "technology", "gadget", "device"]
    }
    
    # Brand mapping
    brand_keywords = {
        "audiotech": ["audiotech", "audio tech", "headphone"],
        "techwatch": ["techwatch", "tech watch", "smartwatch", "watch"],
        "gamemaster": ["gamemaster", "game master", "gaming", "laptop"],
        "phonetech": ["phonetech", "phone tech", "smartphone", "phone"],
        "soundwave": ["soundwave", "sound wave", "speaker"],
        "gamergear": ["gamergear", "gamer gear", "mouse", "gaming mouse"],
        "keymaster": ["keymaster", "key master", "keyboard"],
        "tabletpro": ["tabletpro", "tablet pro", "tablet", "ipad"]
    }
    
    # Extract category
    for cat, keywords_list in category_keywords.items():
        if any(keyword in message_lower for keyword in keywords_list):
            category = cat
            break
    
    # Extract brand
    for br, keywords_list in brand_keywords.items():
        if any(keyword in message_lower for keyword in keywords_list):
            brand = br
            break
    
    # Extract price range (simple regex-like matching)
    import re
    price_patterns = [
        r'under\s*\$?(\d+(?:,\d{3})*)',
        r'below\s*\$?(\d+(?:,\d{3})*)',
        r'less than\s*\$?(\d+(?:,\d{3})*)',
        r'maximum\s*\$?(\d+(?:,\d{3})*)',
        r'max\s*\$?(\d+(?:,\d{3})*)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, message_lower)
        if match:
            price_str = match.group(1).replace(',', '')
            max_price = convert_price_to_usd(price_str)
            break
    
    # Search products
    products = search_products(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        keywords=keywords if keywords else None
    )
    
    # Generate response
    if products:
        product_list = "\n".join([
            f"• {product.name} - {product.brand} - ${product.price:.2f}"
            for product in products[:5]
        ])
        response_text = f"I found {len(products)} products matching your search:\n\n{product_list}"
        if len(products) > 5:
            response_text += f"\n\n... and {len(products) - 5} more products."
    else:
        response_text = "I couldn't find any products matching your criteria. Try different search terms."
    
    return {
        "response": response_text,
        "products": [product.model_dump() for product in products],
        "search_params": {
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price
        }
    }
