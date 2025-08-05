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
    
    # Filter by keywords in name or description
    if keywords:
        for keyword in keywords:
            filtered_products = [
                p for p in filtered_products 
                if keyword.lower() in p.name.lower() or keyword.lower() in p.description.lower()
            ]
    
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
                        "description": "Product category (e.g., 'Điện thoại', 'Laptop', 'Tai nghe', 'Máy ảnh', 'TV', 'Máy chơi game')"
                    },
                    "brand": {
                        "type": "string", 
                        "description": "Product brand (e.g., 'Apple', 'Samsung', 'Sony', 'Dell', 'LG', 'Nintendo')"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price in VND"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in VND"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search in product name and description"
                    }
                },
                "required": []
            }
        }
    }
]

def convert_price_to_vnd(price_str: str) -> Optional[float]:
    """Convert price string with various formats to VND"""
    if not price_str:
        return None
    
    # Remove currency symbols and normalize
    price_str = price_str.replace('$', '').replace(',', '').replace(' ', '').lower()
    
    try:
        price = float(price_str)
        # If it looks like USD (typically under 10000), convert to VND
        if price < 10000:
            return price * 25000  # Approximate USD to VND conversion
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
        
        Available categories: Điện thoại (phones), Laptop, Tai nghe (headphones), Máy ảnh (cameras), TV, Máy chơi game (gaming consoles)
        Available brands: Apple, Samsung, Sony, Dell, LG, Nintendo, Canon
        
        Convert USD prices to VND (multiply by 25,000). Extract category, brand, price range, and relevant keywords from user queries."""
        
        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
                    f"• {product.name} - {product.brand} - {product.price:,.0f} VND"
                    for product in products[:5]
                ])
                response_text = f"I found {len(products)} products matching your criteria:\n\n{product_list}"
                if len(products) > 5:
                    response_text += f"\n\n... and {len(products) - 5} more products."
            else:
                response_text = "I couldn't find any products matching your criteria. Try adjusting your search terms."
            
            return {
                "response": response_text,
                "products": [product.dict() for product in products],
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
        "điện thoại": ["phone", "điện thoại", "iphone", "smartphone"],
        "laptop": ["laptop", "máy tính", "computer"],
        "tai nghe": ["headphone", "tai nghe", "earphone"],
        "máy ảnh": ["camera", "máy ảnh"],
        "tv": ["tv", "television", "tivi"],
        "máy chơi game": ["gaming", "console", "nintendo", "switch"]
    }
    
    # Brand mapping
    brand_keywords = {
        "apple": ["apple", "iphone", "macbook"],
        "samsung": ["samsung", "galaxy"],
        "sony": ["sony"],
        "dell": ["dell"],
        "lg": ["lg"],
        "nintendo": ["nintendo", "switch"]
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
            max_price = convert_price_to_vnd(price_str)
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
            f"• {product.name} - {product.brand} - {product.price:,.0f} VND"
            for product in products[:5]
        ])
        response_text = f"I found {len(products)} products matching your search:\n\n{product_list}"
        if len(products) > 5:
            response_text += f"\n\n... and {len(products) - 5} more products."
    else:
        response_text = "I couldn't find any products matching your criteria. Try different search terms."
    
    return {
        "response": response_text,
        "products": [product.dict() for product in products],
        "search_params": {
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price
        }
    }
