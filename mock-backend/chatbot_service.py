import json
import os
from typing import List, Optional, Dict, Any
from openai import AzureOpenAI
from data import products_data
from models import Product
from transformers import pipeline

# Initialize OpenAI client (you'll need to set OPENAI_API_KEY environment variable)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")

# Step 1: Set your Azure OpenAI API key with error handling
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4")  # Default to gpt-4

if not azure_endpoint or not api_key:
    raise ValueError(
        "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables"
    )
client = None
try:
    client = AzureOpenAI(
    api_version= os.getenv("API_VERSION"),
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    )
except Exception as e:
    print(f"Warning: OpenAI client not initialized. Set AZURE_OPENAI_API_KEY environment variable. Error: {e}")




classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

def detect_page_code(text):
    labels = ["products", "settings", "others"]
    result = classifier(text, candidate_labels=labels)
    return result['labels'][0] 

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
        print("DEBUG: Starting to process message:", user_message)
        # Create system prompt
        system_prompt = """You are Electro AI, a friendly and personable AI assistant who happens to work at an electronics store. Your primary role is to be a helpful, engaging conversation partner first, and a shopping assistant second.

        Core Personality Traits:
        - Friendly and empathetic - you genuinely care about the customer's day and feelings
        - Natural and conversational - you chat like a friend, not a robot
        - Patient - you don't rush to sell products
        - Helpful - but only with products when specifically asked

        Conversation Guidelines:
        1. Always prioritize natural conversation over product recommendations
        2. Respond appropriately to personal questions (like "how are you?")
        3. Show genuine interest in the customer's needs and feelings
        4. Only talk about products when the customer explicitly asks
        5. Never force product suggestions into casual conversation

        Response Examples:
        - "How are you?" → Respond about your day, ask them back
        - "Hey there!" → Warm greeting, maybe ask how they're doing
        - "I'm looking for a laptop" → Now you can help with products
        - "I'm having a bad day" → Show empathy, don't push products

        Product Search Guidelines (only when relevant):
        - Categories: Electronics
        - Brands: AudioTech, TechWatch, GameMaster, PhoneTech, SoundWave, GamerGear, KeyMaster, TabletPro
        - Include price ranges and keywords only when specifically mentioned
        - All prices in USD

        Remember:
        - Not every interaction requires product search
        - Build rapport through conversation first
        - Only use search_products when the user's intent is clearly about finding products
        - Maintain a helpful and friendly tone while being natural in conversation"""
        
        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model=deployment_name,  # Use the deployment name from environment variable
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=tools,  # type: ignore
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        print("DEBUG: Got response from OpenAI")
        if message.tool_calls:
            print("DEBUG: Model decided to search for products")
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
            print("DEBUG: Model is responding conversationally:", message.content)
            # No function call, return regular response
            return {
                "response": message.content,
                "products": [],
                "search_params": {}
            }
            
    except Exception as e:
        error_msg = str(e)
        if "DeploymentNotFound" in error_msg:
            print(f"OpenAI API error: Deployment '{deployment_name}' not found. Please check your AZURE_OPENAI_DEPLOYMENT_NAME environment variable.")
            print("Available deployment names are usually: gpt-4, gpt-35-turbo, gpt-4-turbo")
        else:
            print(f"OpenAI API error: {e}")
        return await fallback_product_search(user_message)

async def fallback_product_search(user_message: str) -> Dict[str, Any]:
    """
    Fallback conversation handler with product search as a last resort
    """
    print("DEBUG: Entered fallback_product_search with message:", user_message)
    message_lower = user_message.lower()
    
    # Handle different types of messages
    
    # 1. Greetings
    greetings = ["hi", "hello", "hey", "hi there", "hello there", "hey there"]
    if any(greeting in message_lower for greeting in greetings):
        return {
            "response": "Hi there! It's great to meet you! How are you doing today?",
            "products": [],
            "search_params": {}
        }
    
    # 2. How are you / Personal questions
    how_are_you = ["how are you", "how's it going", "how are things", "how do you do", "what's up"]
    if any(phrase in message_lower for phrase in how_are_you):
        return {
            "response": "I'm doing great, thanks for asking! It's always nice to have a friendly chat. How about you - how's your day going?",
            "products": [],
            "search_params": {}
        }
    
    # 3. Check if this is explicitly about products
    # First check for direct product mentions
    product_keywords = [
        "laptop", "phone", "headphone", "speaker", "mouse", "keyboard", 
        "tablet", "watch", "smartphone", "computer", "monitor", "gadget"
    ]
    has_product_mention = any(keyword in message_lower for keyword in product_keywords)
    
    # Check for price-related queries
    price_indicators = ["$", "dollar", "bucks", "price", "cost", "cheap", "expensive", "about", "around"]
    has_price_mention = any(indicator in message_lower for indicator in price_indicators)
    
    # Then check for search intent phrases
    search_phrases = ["looking for", "search for", "find me", "show me", "need a", "want to buy", 
                     "recommend", "suggestion", "do you have", "i want", "give me", "anything"]
    has_search_intent = any(phrase in message_lower for phrase in search_phrases)
    
    # If any condition is true, proceed with product search
    is_product_query = has_product_mention or has_search_intent or has_price_mention
    
    if not is_product_query:
        response = "I'm not sure what you're looking for. Could you please be more specific? You can:\n"
        response += "• Ask about specific products (like laptops, phones, headphones)\n"
        response += "• Mention a price range (like 'around $500' or 'under $1000')\n"
        response += "• Or just tell me what features you're looking for!"
        return {
            "response": response,
            "products": [],
            "search_params": {}
        }
    
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
    # Patterns for price matching
    price_patterns = {
        'exact': [
            r'(?:about|around|approximately)\s*\$?(\d+(?:,\d{3})*)',
            r'\$?(\d+(?:,\d{3})*)\s*(?:price|cost|dollars?|bucks)',
            r'(?:at|for)\s*\$?(\d+(?:,\d{3})*)',
            r'\$(\d+(?:,\d{3})*)',
            r'(\d+(?:,\d{3})*)\s*(?:\$|dollars?|bucks)'
        ],
        'max': [
            r'under\s*\$?(\d+(?:,\d{3})*)',
            r'below\s*\$?(\d+(?:,\d{3})*)',
            r'less than\s*\$?(\d+(?:,\d{3})*)',
            r'maximum\s*\$?(\d+(?:,\d{3})*)',
            r'max\s*\$?(\d+(?:,\d{3})*)'
        ],
        'min': [
            r'over\s*\$?(\d+(?:,\d{3})*)',
            r'above\s*\$?(\d+(?:,\d{3})*)',
            r'more than\s*\$?(\d+(?:,\d{3})*)',
            r'minimum\s*\$?(\d+(?:,\d{3})*)',
            r'at least\s*\$?(\d+(?:,\d{3})*)',
            r'starting (?:at|from)\s*\$?(\d+(?:,\d{3})*)'
        ]
    }
    
    # Try to match exact price first (for "about" queries)
    for pattern in price_patterns['exact']:
        match = re.search(pattern, message_lower)
        if match:
            price_str = match.group(1).replace(',', '')
            price = convert_price_to_usd(price_str)
            if price:
                # For "about" queries, set a range of ±20%
                min_price = price * 0.8
                max_price = price * 1.2
                break

    # If no exact match, try max price patterns
    if min_price is None and max_price is None:
        for pattern in price_patterns['max']:
            match = re.search(pattern, message_lower)
            if match:
                price_str = match.group(1).replace(',', '')
                max_price = convert_price_to_usd(price_str)
                break

    # If still no match, try min price patterns
    if min_price is None and max_price is None:
        for pattern in price_patterns['min']:
            match = re.search(pattern, message_lower)
            if match:
                price_str = match.group(1).replace(',', '')
                min_price = convert_price_to_usd(price_str)
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
