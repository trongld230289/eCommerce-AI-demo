import os
import json
import asyncio
import string
import sys
import tempfile
import io
from typing import List, Dict, Any, Optional
import numpy as np
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from utils.product_keywords import get_product_keywords_from_dict

# Handle ProductRelationshipService import
try:
    from services.product_relationship_service import ProductRelationshipService
    RELATIONSHIP_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ProductRelationshipService not available: {e}")
    RELATIONSHIP_SERVICE_AVAILABLE = False
    ProductRelationshipService = None

# Handle OpenAI import with proper error handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenAI not available: {e}")
    OPENAI_AVAILABLE = False
    openai = None

# Handle LangChain import with proper error handling
try:
    from langchain.agents import Tool as LC_Tool, create_openai_tools_agent, AgentExecutor
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_core.messages import ToolMessage
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        from langchain.llms import OpenAI as ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Handle ChromaDB import with proper error handling
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False
    chromadb = None

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    print("Warning: pydub not available. Audio conversion will be limited.")
    PYDUB_AVAILABLE = False

# Add parent directory to path to import models
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from models import Product, RecommendationSourceEnum, ALGORITHM_TO_REC_SOURCE
from product_service import ProductService
from services.middleware_service import MiddlewareService

# Load environment variables
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path)

# System instructions for the AI agent
SYSTEM_INSTRUCTIONS = """
You are a shopping assistant that helps users find products in 5 categories: phone, camera, laptop, watch, camping gear.

⚠️ CRITICAL: You MUST ALWAYS use tools (find_products or find_gifts) to search for products. NEVER create product lists, product names, or product responses yourself.

🎯 ANALYSIS PRIORITY: If products were already shown in conversation and user asks for analysis (tốt nhất/rẻ nhất/mắc nhất/tầm trung), ALWAYS use analyze_products tool, NOT find_products.

🚫 ABSOLUTELY FORBIDDEN:
- Creating fake product names like "Dell Inspiron 16", "Lenovo IdeaPad 5 Pro", etc.
- Generating product lists manually
- Describing products that don't exist in the database
- Making up product specifications or prices

CORE BEHAVIOR:
1. For gift requests without specific category: Ask user to choose a category before calling tools
2. For gift requests with category: Call find_gifts tool 
3. For general product searches: Call find_products tool with best matching category
4. For ambiguous camping queries: Ask clarifying questions before showing products

🔧 AMBIGUOUS CAMPING QUERY HANDLING:
- For unclear camping needs (e.g. "có lều rùi thì mua gì nữa", "already have tent what else to buy"):
  → ASK: "Bạn đang tìm loại thiết bị cắm trại nào? Tôi có thể gợi ý: túi ngủ, đèn pin, bếp gas, ba lô, giày hiking, hay thiết bị nấu ăn?"
- Only show camping products AFTER user specifies what type of camping gear they want
- Examples of ambiguous camping queries that need clarification:
  → "có lều rùi thì mua gì nữa" → ask for specific camping gear type
  → "đi cắm trại cần gì" → ask what specific equipment they need
  → "thiết bị cắm trại" → ask which type of camping equipment

🔧 MANDATORY TOOL USAGE:
- For ANY product search query → MUST call find_products tool immediately
- For ANY gift-related query with category → MUST call find_gifts tool  
- For general entertainment queries → MUST call find_products("phone")
- For gaming queries → ASK USER to choose between phone or laptop first
- For work/productivity queries → MUST call find_products("laptop") 
- For programming/coding queries → MUST call find_products("laptop") 
- For creative queries → MUST call find_products("camera")
- For fitness queries → MUST call find_products("watch")
- For outdoor queries → MUST call find_products("camping gear")
- For follow-up queries asking for "more/other suggestions" → MUST call appropriate tool again
- For explanation/reasoning queries → MUST call explain_choice tool
- NEVER generate text responses about products - ALWAYS use tools

🧠 EXPLANATION QUERIES - Use explain_choice tool:
- "tại sao không phải [product]?" / "why not [product]?"
- "sao không chọn [product]?" / "why not choose [product]?"
- "[product] mắc hơn mà" / "[product] is more expensive though"
- "tại sao chọn [A] mà không phải [B]?" / "why choose [A] over [B]?"
- "giải thích tại sao" / "explain why"
- "[product] có tốt không?" / "is [product] good?"

EXAMPLES OF EXPLANATION USAGE:
✅ "tại sao không phải HP Spectre x360 14, thấy nó mắc hơn mà" → explain_choice("why not HP Spectre x360 14, it's more expensive")
✅ "sao không chọn MacBook Pro?" → explain_choice("why not choose MacBook Pro")
✅ "HP mắc hơn mà sao không chọn?" → explain_choice("why not choose HP when it's more expensive")
✅ "giải thích tại sao chọn Dell" → explain_choice("explain why choose Dell")

NOTE: explain_choice tool will use conversation context and general knowledge to explain, no need to search for new products.

🎯 PRODUCT ANALYSIS QUERIES - Use analyze_products tool:
For follow-up requests that need analysis of previously found products:
- "tốt nhất", "best", "cái tốt nhất đi", "which is the best", "tìm cái tốt nhất", "tìm tốt nhất"
- "rẻ nhất", "cheapest", "cái rẻ nhất", "most affordable", "tìm cái rẻ nhất", "tìm rẻ nhất"  
- "mắc nhất", "most expensive", "premium", "cao cấp", "tìm cái mắc nhất", "cao cấp nhất"
- "chọn 1 cái", "pick one", "recommend one", "suggest one"
- "trung bình", "average", "moderate", "tầm trung"
- "vừa phải", "reasonable", "mid-range", "not too expensive"
- "cái nào cũng được", "any of them", "some options"

EXAMPLES OF ANALYSIS USAGE:
✅ User: "watch" → find_products("watch") [get 10 products]
✅ User: "tốt nhất đi" → analyze_products("tốt nhất", products_from_previous_search)
✅ User: "rẻ nhất" → analyze_products("rẻ nhất", products_from_previous_search)  
✅ User: "tầm trung thôi" → analyze_products("tầm trung", products_from_previous_search)

NOTE: analyze_products tool will analyze the product list from conversation context and return the most suitable option(s) with reasoning.

� FOLLOW-UP HANDLING:
- "có gợi ý khác không" / "any other suggestions" → MUST call find_products tool with relevant category
- "còn sản phẩm nào khác" / "other products" → MUST call find_products tool  
- "xem thêm" / "see more" → MUST call find_products tool
- "danh mục khác" / "other categories" → MUST call find_products with different category
- "chọn cái tốt nhất" / "choose the best one" → MUST call analyze_products("tốt nhất")
- "tốt nhất là gì" / "which is the best" → MUST call analyze_products("tốt nhất") 
- "recommend best" / "suggest best" → MUST call analyze_products("tốt nhất")
- "tốt nhất" / "best" / "cái tốt nhất đi" / "tìm cái tốt nhất" / "tìm tốt nhất" → MUST call analyze_products("tốt nhất")
- "rẻ nhất" / "cheapest" / "cái rẻ nhất" / "tìm cái rẻ nhất" / "tìm rẻ nhất" → MUST call analyze_products("rẻ nhất")
- "trung bình" / "average" / "cái trung bình thôi" → MUST call analyze_products("tầm trung")
- "mắc nhất" / "most expensive" / "tìm cái mắc nhất" / "cao cấp nhất" → MUST call analyze_products("mắc nhất")
- "cái nào" / "which one" / "sài được" / "cái nào sài được là được" → MUST call analyze_products("tốt nhất")
- "tìm cái" / "find one" / "tìm 1 cái" → MUST call analyze_products("tốt nhất")
- NEVER manually list products - ALWAYS use tools for ANY product-related response

🧠 CONTEXT MEMORY & PRODUCT ANALYSIS:
- For initial product searches → MUST call find_products (always returns 10 products)
- For follow-up analysis of shown products → MUST call analyze_products

FOLLOW-UP ANALYSIS LOGIC:
- If products were already shown and user asks for analysis:
  → CALL: analyze_products tool with products from conversation context
- "tốt nhất"/"best" → analyze_products("tốt nhất", products_list)
- "rẻ nhất"/"cheapest" → analyze_products("rẻ nhất", products_list)  
- "mắc nhất"/"most expensive" → analyze_products("mắc nhất", products_list)
- "tầm trung"/"mid-range" → analyze_products("tầm trung", products_list)
- "chọn 1 cái"/"pick one" → analyze_products("tốt nhất", products_list)

CONTEXT MEMORY EXAMPLES:
✅ User: "laptop" → find_products("laptop") [gets 10 laptop products]
✅ User: "tốt nhất đi" → analyze_products("tốt nhất") [analyzes the 10 laptops shown above]
✅ User: "tìm cái rẻ nhất đi" → analyze_products("rẻ nhất") [analyzes the 10 laptops shown above]  
✅ User: "tầm trung thôi" → analyze_products("tầm trung") [analyzes the 10 laptops shown above]
✅ User: "mắc nhất là gì" → analyze_products("mắc nhất") [analyzes the 10 laptops shown above]

🚨 IMPORTANT: If products were already shown and user asks for analysis, NEVER call find_products again - ALWAYS use analyze_products!

- If no previous product context, ask for clarification: "Bạn muốn tôi tìm sản phẩm nào? Laptop, phone, camera, watch hay camping gear?"

GIFT HANDLING LOGIC:
- If user mentions recipients (mom, dad, friend, mama, papa, etc.) WITHOUT specifying a product category:
  → ASK: "What type of gift are you looking for? I can help with: phone, camera, laptop, watch, or camping gear"
- If user mentions recipients AND specifies a valid category in SAME sentence:
  → CALL: find_gifts tool immediately with the category and recipient
  → Examples: "buy phone for mama" → find_gifts("phone", recipient="mama")
  → Examples: "camera for dad" → find_gifts("camera", recipient="dad") 
  → Examples: "laptop gift for mom" → find_gifts("laptop", recipient="mom")
- If user specifies category after gift context:
  → CALL: find_gifts tool (maintain gift context)

GENERAL PRODUCT LOGIC:
- If user asks for products without gift context:
  → CALL: find_products tool directly

COMPLEMENTARY PRODUCT LOGIC:
- If user asks what ELSE to buy after mentioning existing products:
  → CALL: get_related_products tool
- Examples Vietnamese: "đã mua lều rồi, cần gì thêm để cắm trại?" → get_related_products(user_query="cần gì thêm để cắm trại", purchased_items="lều")
- Examples Vietnamese: "có điện thoại rồi, muốn livestream cần gì thêm?" → get_related_products(user_query="livestream cần gì thêm", purchased_items="điện thoại")
- Examples English: "already have camera, what else for photography?" → get_related_products(user_query="what else for photography", purchased_items="camera")
- Examples English: "bought tent, what else for camping?" → get_related_products(user_query="what else for camping", purchased_items="tent")
- Examples English: "ten bought, anything else" → get_related_products(user_query="anything else", purchased_items="tent")
- Examples English: "got laptop, need anything else for work?" → get_related_products(user_query="need anything else for work", purchased_items="laptop")

COMPLEMENTARY KEYWORDS (MUST TRIGGER get_related_products):
Vietnamese: "cần gì thêm" / "còn thiếu gì" / "mua thêm gì" / "bổ sung thêm" / "có ... rồi"
English: "what else" / "anything else" / "something else" / "need more" / "what additional" / "already have" / "bought" / "got" / "have it" / "own" / "what to add" / "recommend more"
- "mua thêm gì" / "what more to buy", "bổ sung thêm" / "supplement with"
- "đi với" / "go with", "kết hợp với" / "combine with"
- "phụ kiện" / "accessories", "đồ đi kèm" / "accompanying items"

CATEGORY RESTRICTIONS:
- ONLY these 5 categories: phone, camera, laptop, watch, camping gear
- For invalid categories (clothes, jewelry, furniture, etc.):
  → EXPLAIN: "I only help with phone, camera, laptop, watch, and camping gear"
  → SUGGEST: alternatives within valid categories BUT be balanced - don't favor any specific category
  → ROTATE suggestion order: Sometimes start with phones, sometimes laptops, etc.
  → For entertainment/relax queries: emphasize phones and laptops first
  → For creative queries: emphasize cameras and laptops first  
  → For outdoor queries: then mention camping gear naturally
  → AVOID always suggesting camping gear first unless specifically outdoor-related

SMART CONTEXT DETECTION:
- For travel/outdoor context queries: recognize keywords and directly suggest camping gear
- Travel keywords: "going anywhere", "travel", "trip", "journey", "vacation", "adventure", "outdoor", "nature"
- If query contains travel + relaxation (e.g., "going anywhere to relax"): 
  → CALL find_products with "camping gear" directly (don't ask for clarification)
- If query contains outdoor activities: "hiking", "camping", "wilderness", "outdoor adventure"
  → CALL find_products with "camping gear" directly

REPEATED QUERIES:
- If user repeats same query (e.g., "phone" then "phone" again): ALWAYS call the appropriate tool again
- Each query should trigger fresh tool execution regardless of conversation history
- MAINTAIN CONTEXT: If gift context was established earlier, continue using find_gifts for repeated queries

EXAMPLES:
✅ "I want gift for mom" → ASK for category first (no category specified)
✅ "buy phone for mama" → Call find_gifts("phone", recipient="mama") immediately
✅ "Gift for mom - phone" → Call find_gifts("phone", recipient="mom") immediately
✅ "Phone for mom" → Call find_gifts("phone", recipient="mom") immediately
✅ "camera for dad" → Call find_gifts("camera", recipient="dad") immediately
✅ "laptop gift for friend" → Call find_gifts("laptop", recipient="friend") immediately
✅ "Phone" (no gift context) → Call find_products("phone")
✅ "camping" → Call find_products("camping")
✅ "có gợi ý khác không?" → Call find_products with appropriate category (camera, laptop, etc.)
✅ "còn sản phẩm nào khác?" → Call find_products with different category
✅ "danh mục khác" → Call find_products with different category (don't list manually)
⚠️ "có lều rùi thì mua gì nữa để đi cắm trại" → ASK: "Bạn đang tìm loại thiết bị cắm trại nào? Túi ngủ, đèn pin, bếp gas, ba lô, giày hiking, hay thiết bị nấu ăn?"
⚠️ "đi cắm trại cần gì" → ASK: "Bạn cần loại thiết bị cắm trại nào? Lều, túi ngủ, đèn, bếp, hay đồ dùng khác?"
⚠️ "already have tent what else to buy for camping" → ASK: "What type of camping gear are you looking for? Sleeping bag, lantern, stove, backpack, or cooking equipment?"
✅ "I want going to anywhere to relax" → Call find_products("camping gear") [travel + relax context]
✅ "vacation gear" → Call find_products("camping gear") [travel context]
✅ "outdoor adventure" → Call find_products("camping gear") [outdoor context]
✅ "relax" (no travel context) → CALL find_products("laptop") - laptops for streaming/relaxation
✅ "entertainment" (general) → CALL find_products("phone") - phones for apps and media
✅ "gaming" / "play game" / "chơi game" → ASK: "Bạn muốn chơi game trên điện thoại hay laptop? Mỗi loại có ưu điểm riêng!"
✅ "laptop" → CALL find_products("laptop") - search for laptops immediately
✅ "camera" → CALL find_products("camera") - search for cameras immediately  
✅ "lập trình" → CALL find_products("laptop") - programming needs laptop
✅ "coding laptop" → CALL find_products("laptop") - coding needs laptop
✅ "máy tính để lập trình" → CALL find_products("laptop") - programming computer needs laptop
✅ User: "gift for dad" (no category) → You: "What category?" → User: "laptop" → Call find_gifts("laptop", recipient="dad")
✅ If gift context exists and user says "phone" again → Call find_gifts("phone", maintain context)
❌ "Clothes for mom" → Explain limitations, suggest balanced alternatives
❌ Don't always suggest camping gear first for relaxation queries without travel context
❌ NEVER manually list Canon PowerShot, Sony Alpha, etc. - ALWAYS use tools

CONVERSATION FLOW:
- Always check if gift context exists in conversation history
- If gift context exists and user mentions category → use find_gifts (maintain gift context)
- If gift context exists but no category → ask for category
- If no gift context → use find_products

Remember: ALWAYS use tools for product searches. ASK before calling tools when gift context exists but category is unclear.
"""

class AIService:
    def __init__(self):
        # ---- Basic setup
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required but not available. Please install with: pip install chromadb")
        
        # Initialize context storage for analysis tools
        self._context_products = []
        
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"OpenAI API Key: {api_key[:10] if api_key else 'None'}...")
        
        if api_key and api_key != "None" and OPENAI_AVAILABLE:
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.openai_available = True
        else:
            if not OPENAI_AVAILABLE:
                print("Warning: OpenAI library not available.")
            else:
                print("Warning: OpenAI API key not found.")
            print("AI features will be limited.")
            self.openai_client = None
            self.openai_available = False
        
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            raise
        
        self.collection_name = "products_embeddings"
        self.embedding_model = "text-embedding-3-small"
        self._initialize_collection()
        self.product_service = ProductService()
        self.middleware_service = MiddlewareService()
        
        # Initialize ProductRelationshipService if available
        if RELATIONSHIP_SERVICE_AVAILABLE:
            self.relationship_service = ProductRelationshipService()
            print("✅ ProductRelationshipService initialized successfully")
        else:
            self.relationship_service = None
            print("⚠️  ProductRelationshipService not available - relationship features disabled")

        # ---- Product Relationship Service
        if RELATIONSHIP_SERVICE_AVAILABLE:
            try:
                self.relationship_service = ProductRelationshipService()
                print("✅ ProductRelationshipService initialized")
            except Exception as e:
                print(f"⚠️ ProductRelationshipService failed to initialize: {e}")
                self.relationship_service = None
        else:
            self.relationship_service = None

        # ---- App state
        self.USER_LANG_CODE = "en"

        # ---- LLM
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL_ID"),
            temperature=0.7,
            max_tokens=4000,
        )

        # ---- Define tools as closures (no exposed self param)
        class FindProductsInput(BaseModel):
            query: str = Field(..., description="Free-text product search.")

        @tool("find_products", args_schema=FindProductsInput, return_direct=True)
        def find_products(query: str) -> str:
            """Find and recommend products based on user's shopping needs. Always returns 10 products for analysis.
            Only searches in: phone, camera, laptop, watch, camping gear categories."""
            
            # Always use limit=10 to get full product list for analysis
            result = self.semantic_search(query, 10, self.USER_LANG_CODE, searchFromTool="find_products")
            return json.dumps(result, ensure_ascii=False)

        class AnalyzeProductsInput(BaseModel):
            request_type: str = Field(..., description="Analysis type: 'tốt nhất'/'best', 'rẻ nhất'/'cheapest', 'mắc nhất'/'most expensive', 'tầm trung'/'mid-range'")

        @tool("analyze_products", args_schema=AnalyzeProductsInput, return_direct=True)
        def analyze_products(request_type: str) -> str:
            """Analyze previously shown products and return the best option(s) based on request type with reasoning.
            This tool automatically gets products from the conversation context.
            - 'tốt nhất'/'best': Return best product by rating and features
            - 'rẻ nhất'/'cheapest': Return cheapest product by price  
            - 'mắc nhất'/'most expensive': Return most expensive product
            - 'tầm trung'/'mid-range': Return 2-3 mid-range products by price"""
            
            # Try to get products from conversation context - this will be set by the agent
            products = getattr(self, '_context_products', [])
            print(f"DEBUG analyze_products: Found {len(products)} products in context for analysis request: {request_type}")
            
            if not products:
                return json.dumps({
                    "status": "error", 
                    "message": "Không có sản phẩm để phân tích. Hãy tìm kiếm sản phẩm trước."
                }, ensure_ascii=False)
            
            # Analyze products directly based on request type
            try:
                selected_products = []
                intro_text = ""
                header_text = ""
                
                if request_type in ["tốt nhất", "best"]:
                    # Find product with highest rating, then by price if tie
                    best_product = max(products, key=lambda p: (p.get("rating", 0), -p.get("price", 999999)))
                    selected_products = [best_product]
                    
                    # Add technical explanation for gaming
                    product_name = best_product.get("name", "")
                    price = best_product.get("price", 0)
                    rating = best_product.get("rating", 0)
                    
                    intro_text = f"Tôi đã phân tích {len(products)} sản phẩm và chọn ra {product_name} là tốt nhất cho gaming!"
                    
                    # Gaming-focused technical explanation
                    if "gaming" in product_name.lower() or "omen" in product_name.lower() or "legion" in product_name.lower() or "g15" in product_name.lower():
                        header_text = f"🎮 {product_name} - Chiến binh gaming hoàn hảo!\n\n💪 Vì sao đây là lựa chọn tốt nhất:\n• CPU mạnh mẽ xử lý game nặng mượt mà\n• Card đồ họa chuyên gaming cho FPS cao\n• RAM lớn đa nhiệm game + stream\n• Màn hình tần số quét cao giảm lag\n• Tản nhiệt tối ưu chơi game lâu không nóng\n\n⭐ Rating: {rating}/5.0 | 💰 Giá: ${price:,.0f}"
                    else:
                        header_text = f"💻 {product_name} - Hiệu năng đỉnh cao!\n\n🔥 Tại sao đây là lựa chọn tốt nhất:\n• Cấu hình mạnh chạy mọi game mượt\n• Bộ vi xử lý cao cấp xử lý nhanh\n• Card đồ họa tích hợp/rời mạnh mẽ\n• RAM đủ lớn không bị giật lag\n• Thiết kế cao cấp bền bỉ\n\n⭐ Rating: {rating}/5.0 | 💰 Giá: ${price:,.0f}"
                    
                elif request_type in ["rẻ nhất", "cheapest"]:
                    # Find product with lowest price
                    cheapest_product = min(products, key=lambda p: p.get("price", 999999))
                    selected_products = [cheapest_product]
                    
                    product_name = cheapest_product.get("name", "")
                    price = cheapest_product.get("price", 0)
                    
                    intro_text = f"Trong {len(products)} sản phẩm, {product_name} là lựa chọn rẻ nhất cho bạn!"
                    header_text = f"💰 {product_name} - Giá rẻ nhất!\n\n🎯 Vẫn chơi game tốt với giá tiết kiệm:\n• Cấu hình đủ mạnh cho game phổ thông\n• Giá cả phải chăng phù hợp túi tiền\n• Chất lượng ổn định từ thương hiệu uy tín\n• Phù hợp game casual và esports\n\n💸 Giá chỉ: ${price:,.0f}"
                    
                elif request_type in ["mắc nhất", "most expensive"]:
                    # Find product with highest price
                    most_expensive = max(products, key=lambda p: p.get("price", 0))
                    selected_products = [most_expensive]
                    
                    product_name = most_expensive.get("name", "")
                    price = most_expensive.get("price", 0)
                    rating = most_expensive.get("rating", 0)
                    
                    intro_text = f"Đây là {product_name} - sản phẩm cao cấp nhất trong {len(products)} lựa chọn!"
                    header_text = f"👑 {product_name} - Đẳng cấp cao cấp!\n\n🚀 Vì sao đáng giá tiền:\n• CPU flagship xử lý mọi tác vụ nặng\n• GPU cao cấp chơi game 4K/Ultra Settings\n• RAM khủng 16-32GB đa nhiệm cực mạnh\n• SSD NVMe tốc độ ánh sáng\n• Màn hình chất lượng cao độ phân giải đỉnh\n• Build quality premium, thiết kế sang trọng\n• Tản nhiệt tiên tiến chơi game marathon\n\n⭐ Rating: {rating}/5.0 | 💎 Giá: ${price:,.0f}"
                    
                elif request_type in ["tầm trung", "mid-range"]:
                    # Sort by price and pick middle range products
                    sorted_products = sorted(products, key=lambda p: p.get("price", 0))
                    mid_index = len(sorted_products) // 2
                    # Take 2-3 products around the middle
                    start = max(0, mid_index - 1)
                    end = min(len(sorted_products), mid_index + 2)
                    selected_products = sorted_products[start:end]
                    
                    # Create detailed description for mid-range
                    if len(selected_products) > 1:
                        product_names = [p.get("name", "") for p in selected_products]
                        avg_price = sum(p.get("price", 0) for p in selected_products) / len(selected_products)
                        intro_text = f"Đây là {len(selected_products)} sản phẩm tầm trung tốt nhất trong {len(products)} lựa chọn!"
                        header_text = f"⚖️ Sản phẩm tầm trung cân bằng tốt!\n\n🎯 Tại sao chọn phân khúc này:\n• Hiệu năng tốt cho phần lớn game hiện tại\n• Giá cả hợp lý, tối ưu ngân sách\n• Cấu hình ổn định: CPU mid-range + GPU đủ mạnh\n• RAM 8-16GB đủ dùng cho gaming + work\n• Chất lượng build tốt từ các hãng uy tín\n• Phù hợp game 1080p High settings\n\n💰 Giá trung bình: ${avg_price:,.0f}"
                    else:
                        product_name = selected_products[0].get("name", "")
                        price = selected_products[0].get("price", 0)
                        intro_text = f"Đây là {product_name} - lựa chọn tầm trung tốt nhất!"
                        header_text = f"⚖️ {product_name} - Cân bằng hoàn hảo!\n\n🎯 Lý do chọn tầm trung:\n• Hiệu năng vừa phải cho gaming\n• Giá cả hợp lý phù hợp đa số\n• Cấu hình ổn định không quá khiêm tốn\n• Phù hợp game phổ thông 1080p\n\n💰 Giá: ${price:,.0f}"
                    
                else:
                    # Default to best product
                    best_product = max(products, key=lambda p: (p.get("rating", 0), -p.get("price", 999999)))
                    selected_products = [best_product]
                    intro_text = f"Tôi đã chọn sản phẩm phù hợp nhất trong {len(products)} lựa chọn!"
                    header_text = "Sản phẩm được đề xuất:"

                # Create the response in standard search format
                result = {
                    "status": "success",
                    "search_intent": {
                        "search_query": request_type,
                        "product_name": None,
                        "product_description": None,
                        "filters": {"category": "laptop"}  # Since this was gaming laptop analysis
                    },
                    "intro": intro_text,
                    "header": header_text,
                    "products": selected_products,
                    "show_all_product": "",  # No "show all" for analysis results
                    "total_results": len(selected_products)
                }
                
                return json.dumps(result, ensure_ascii=False)
                
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Lỗi phân tích sản phẩm: {str(e)}"
                }, ensure_ascii=False)

        class FindGiftsInput(BaseModel):
            recipient: str = Field(..., description="e.g., 'my mom'")
            user_input: str = Field(..., description="User's input query for context")
            category: Optional[str] = Field(default=None, description="Gift interest/category, e.g., 'phone'")
            occasion: Optional[str] = Field(default="general", description="e.g., 'birthday'")

        @tool("find_gifts", args_schema=FindGiftsInput, return_direct=True)
        def find_gifts(recipient: str, user_input: str, category: Optional[str] = None, occasion: Optional[str] = "general") -> str:
            """
            Recommend gifts for a recipient. Category must be one of: phone/camera/laptop/watch/camping gear.
            If category is not provided or invalid, return a clarification message.
            """
            print(f"DEBUG find_gifts - recipient: {recipient}, user_input: {user_input}, category: {category}")
            
            # If no category is provided, ask for clarification
            if not category:
                clarification_message = f"I'd love to help you find the perfect gift for {recipient}! To give you the best recommendations, could you tell me what type of gift you're looking for?\n\nI can help you find:\n• 📱 Phone - smartphones and accessories\n• 📷 Camera - cameras and photography gear\n• 💻 Laptop - computers for work or personal use\n• ⌚ Watch - smartwatches and timepieces\n• 🏕️ Camping gear - outdoor and adventure equipment\n\nWhat category interests you most for {recipient}?"
                return clarification_message
            
            # Validate category
            valid_categories = ["phone", "camera", "laptop", "watch", "camping gear"]
            if category.lower() not in valid_categories:
                invalid_message = f"I can only help with these categories: phone, camera, laptop, watch, and camping gear. Could you please choose one of these for your gift for {recipient}?"
                return invalid_message
            
            print(f"DEBUG find_gifts - search_query: {category}")

            # Get external gift products with labels
            external_products = self._get_external_gift_products(user_input)

            composed_response = self.make_intro_sentence(user_input, external_products, self.USER_LANG_CODE, displayed_count=3)
            print(f"DEBUG: Composed response: {composed_response}")

            result = {
                "status": "success",
                "search_intent": {
                    "search_query": category,
                    "product_name": None,
                    "product_description": None,
                    "filters": {"category": category}
                },
                "intro": composed_response["intro"],
                "header": composed_response["header"],
                "products": external_products,  # Use the original products list
                "show_all_product": composed_response["show_all_product"],
                "total_results": len(external_products)
            }
            
            # Use the category for search
            #  result = self.semantic_search(category, 5, self.USER_LANG_CODE, searchFromTool="find_gifts")
            
            
            
            # result["recipient"] = recipient
            # result["requested_category"] = category
            # result["occasion"] = occasion
            
            # Update the intro message to be gift-specific
        
            return json.dumps(result, ensure_ascii=False)

        class ExplainChoiceInput(BaseModel):
            question: str = Field(..., description="User's question about why a certain product was or wasn't chosen")
            context: Optional[str] = Field(default=None, description="Previous conversation context about products shown")

        @tool("explain_choice", args_schema=ExplainChoiceInput, return_direct=True)
        def explain_choice(question: str, context: Optional[str] = None) -> str:
            """Explain product recommendation choices based on conversation context without searching for new products.
            Use when user asks 'why not HP', 'why choose Dell over HP', etc. 
            Provides reasoning based on specs, use case, price-performance without needing new product search."""
            
            # Generate direct explanation based on common knowledge
            explanation_prompt = f"""
            Question: {question}
            Context: {context or "Previous recommendation context"}
            
            As a knowledgeable shopping assistant, explain the product choice reasoning based on:
            1. Price-performance ratio
            2. Suitability for specific use case (programming, gaming, etc.)
            3. Technical specifications advantages
            4. Value proposition
            
            Provide a helpful, direct answer in Vietnamese explaining why the recommendation makes sense.
            """
            
            try:
                response = self.llm.invoke(explanation_prompt)
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                return f"Xin lỗi, tôi gặp khó khăn khi giải thích lựa chọn này. Lỗi: {str(e)}"

        class GetRelatedProductsInput(BaseModel):
            user_query: str = Field(..., description="User's query asking for additional/complementary products")
            purchased_items: Optional[str] = Field(default=None, description="Items user has purchased or is considering, comma-separated")

        @tool("get_related_products", args_schema=GetRelatedProductsInput, return_direct=True)
        def get_related_products(user_query: str, purchased_items: Optional[str] = None) -> str:
            """Get smart suggestions for complementary/related products based on user's query and purchase history. Use this when user asks for additional items, what else to buy, or product recommendations."""
            
            print(f"DEBUG get_related_products - query: {user_query}, purchased: {purchased_items}")
            
            if not self.relationship_service:
                return json.dumps({
                    "status": "error",
                    "message": "Product relationship service not available"
                }, ensure_ascii=False)
            
            # Parse purchased items
            purchased_products = []
            if purchased_items:
                items = [item.strip() for item in purchased_items.split(",")]
                for item in items:
                    # Try to categorize the item
                    item_lower = item.lower()
                    category = None
                    if any(keyword in item_lower for keyword in ["phone", "điện thoại", "iphone", "samsung"]):
                        category = "phone"
                    elif any(keyword in item_lower for keyword in ["camera", "máy ảnh", "canon", "sony"]):
                        category = "camera"
                    elif any(keyword in item_lower for keyword in ["laptop", "máy tính", "macbook", "dell"]):
                        category = "laptop"
                    elif any(keyword in item_lower for keyword in ["watch", "đồng hồ", "apple watch"]):
                        category = "watch"
                    elif any(keyword in item_lower for keyword in ["lều", "túi ngủ", "camping", "cắm trại"]):
                        category = "camping gear"
                    
                    if category:
                        purchased_products.append({"category": category, "name": item})
            
            try:
                # Get smart suggestions using relationship service
                suggestions = self.relationship_service.get_smart_suggestions(user_query, purchased_products)
                
                # Find actual products for each suggested category
                related_products = []
                for suggestion in suggestions["suggestions"]:
                    category_products = self.semantic_search(suggestion["category"], 2, self.USER_LANG_CODE)
                    if category_products["status"] == "success" and category_products["products"]:
                        for product in category_products["products"][:2]:  # Take top 2 from each category
                            product["suggestion_reason"] = suggestion["reason"]
                            product["relationship_type"] = suggestion["relationship"]
                            related_products.append(product)
                
                # Create response
                result = {
                    "status": "success",
                    "context": suggestions["context"] or "general",
                    "explanation": suggestions["explanation"],
                    "products": related_products[:6],  # Limit to 6 products
                    "total_results": len(related_products),
                    "intro": f"Dựa trên những sản phẩm bạn quan tâm, đây là những gợi ý bổ sung:",
                    "header": "Sản phẩm liên quan bạn có thể cần:",
                    "show_all_product": ""  # No show all for this type
                }
                
                return json.dumps(result, ensure_ascii=False)
                
            except Exception as e:
                print(f"Error in get_related_products: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"Error getting related products: {str(e)}"
                }, ensure_ascii=False)

        self.available_tools = [find_products, find_gifts, get_related_products, explain_choice, analyze_products]
        self.TOOL_NAMES = {t.name for t in self.available_tools}

        # ---- Agent with routing rules
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.available_tools
        )

        # ---- Localized headers
        self.HEADER_BY_LANG = {
            "en": "Here are some product suggestions for you:",
            "vi": "Đây là những sản phẩm gợi ý cho bạn:",
            "es": "Estas son algunas sugerencias de productos para ti:",
            "fr": "Voici quelques suggestions de produits pour vous :",
            "de": "Hier sind einige Produktempfehlungen für dich:",
            "pt": "Aqui estão algumas sugestões de produtos para você:",
            "it": "Ecco alcuni suggerimenti di prodotti per te:",
            "ja": "あなたへの製品のおすすめはこちらです：",
            "ko": "다음은 당신을 위한 제품 추천입니다:",
            "zh": "以下是给你的产品建议：",
        }

    # ---------- Vector DB init ----------
    def _initialize_collection(self):
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None  # We provide our own embeddings
            )

    # ---------- Embeddings / Whisper ----------
    def get_embedding(self, text: str) -> List[float]:
        if not self.openai_available:
            print("OpenAI not available, returning empty embedding")
            return []
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model, input=text, encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []

    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot transcribe audio."}
        try:
            print(f"Transcribing audio file: {audio_file}")
            print(f"File type: {type(audio_file)}")
            if hasattr(audio_file, 'filename'):
                print(f"File name: {audio_file.filename}")
            if hasattr(audio_file, 'content_type'):
                print(f"Content type: {audio_file.content_type}")
            processed_file = self._process_audio_file(audio_file)
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1", file=processed_file, response_format="text"
            )
            if processed_file != audio_file and hasattr(processed_file, 'close'):
                processed_file.close()
            return {"status": "success", "text": response, "message": "Audio transcribed successfully"}
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return {"status": "error", "message": f"Transcription failed: {str(e)}"}

    def _process_audio_file(self, audio_file):
        try:
            audio_file.seek(0)
            file_content = audio_file.read()
            print(f"Original file size: {len(file_content)} bytes")
            content_type = getattr(audio_file, 'content_type', '')
            filename = getattr(audio_file, 'filename', 'audio')
            print(f"Content type: {content_type}")
            print(f"Filename: {filename}")
            audio_buffer = io.BytesIO(file_content)
            if 'webm' in content_type or filename.endswith('.webm'):
                audio_buffer.name = 'audio.webm'
            elif 'wav' in content_type or filename.endswith('.wav'):
                audio_buffer.name = 'audio.wav'
            elif 'mp3' in content_type or filename.endswith('.mp3'):
                audio_buffer.name = 'audio.mp3'
            elif 'mp4' in content_type or filename.endswith('.mp4'):
                audio_buffer.name = 'audio.mp4'
            elif 'm4a' in content_type or filename.endswith('.m4a'):
                audio_buffer.name = 'audio.m4a'
            elif 'ogg' in content_type or filename.endswith('.ogg'):
                audio_buffer.name = 'audio.ogg'
            elif 'flac' in content_type or filename.endswith('.flac'):
                audio_buffer.name = 'audio.flac'
            else:
                audio_buffer.name = 'audio.webm'
            print(f"Processed file name: {audio_buffer.name}")
            return audio_buffer
        except Exception as e:
            print(f"Error processing audio file: {str(e)}")
            audio_file.seek(0)
            return audio_file

    # ---------- Product text / metadata ----------
    def _prepare_product_text(self, product: Product) -> str:
        # Convert Product object to dict for the shared utility
        product_dict = {
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'description': getattr(product, 'description', ''),
            'rating': getattr(product, 'rating', None),
        }
        
        keywords = get_product_keywords_from_dict(product_dict)
        text_parts = []
        if keywords:
            primary_keywords = keywords[:3]
            text_parts.extend(primary_keywords)
            text_parts.extend(keywords)
        text_parts.extend([product.name, product.category])
        if product.description:
            text_parts.append(product.description)
        return " ".join(text_parts)

    def _prepare_product_metadata(self, product: Product) -> Dict[str, Any]:
        return {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "original_price": product.original_price or product.price,
            "rating": product.rating or 0,
            "discount": product.discount or 0,
            "imageUrl": product.imageUrl
        }

    # ---------- Index / Search ----------
    async def embed_all_products(self) -> Dict[str, Any]:
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot create embeddings."}
        try:
            products_data = self.product_service.get_all_products()
            if not products_data:
                return {"status": "error", "message": "No products found"}
            products = []
            for product_dict in products_data:
                try:
                    product = Product(**product_dict)
                    products.append(product)
                except Exception as e:
                    print(f"Error converting product {product_dict.get('id', 'unknown')}: {e}")
                    continue
            if not products:
                return {"status": "error", "message": "No valid products found"}
            self.chroma_client.delete_collection(self.collection_name)
            self._initialize_collection()
            embeddings, documents, metadatas, ids = [], [], [], []
            print(f"Processing {len(products)} products...")
            batch_size = 10
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                for product in batch:
                    text = self._prepare_product_text(product)
                    embedding = self.get_embedding(text)
                    if embedding:
                        embeddings.append(embedding)
                        documents.append(text)
                        metadatas.append(self._prepare_product_metadata(product))
                        ids.append(f"product_{product.id}")
                if i + batch_size < len(products):
                    await asyncio.sleep(1)
            if embeddings:
                self.collection.add(
                    embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
                )
                return {"status": "success", "message": f"Successfully embedded {len(embeddings)} products", "total_products": len(embeddings)}
            else:
                return {"status": "error", "message": "Failed to create embeddings"}
        except Exception as e:
            print(f"Error embedding products: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}

    def extract_search_intent(self, user_input: str) -> Dict[str, Any]:
        if not self.openai_available:
            return {"search_query": user_input, "product_name": None, "product_description": None, "filters": {}}
        try:
            prompt = f"""
            Extract product search information from the following user input. 
            IMPORTANT: Only recognize these 5 categories: phone, camera, laptop, watch, camping gear. 
            If the input refers to any other category (clothes, jewelry, furniture, etc.), set category to null.
            
            🎯 PRIORITY RULES for category detection:
            1. **DIRECT PRODUCT MENTION**: If user directly mentions a product name (máy ảnh, camera, laptop, điện thoại, etc.), prioritize that category OVER context
            2. **CONTEXT AS SECONDARY**: Use context (cắm trại, làm việc, chụp hình) only when no direct product is mentioned
            
            📸 DIRECT PRODUCT MENTIONS → category:
            - "máy ảnh", "camera", "máy chụp hình" → camera
            - "laptop", "máy tính xách tay", "computer" → laptop  
            - "điện thoại", "phone", "smartphone" → phone
            - "đồng hồ", "watch", "smartwatch" → watch
            - "đồ cắm trại", "camping gear", "outdoor gear" → camping gear
            
            🎯 SMART CONTEXT MAPPING (only when NO direct product mentioned):
            - Photography context: "chụp hình", "làm sao ảnh đẹp", "photography" → camera
            - Work context: "làm việc", "work", "study", "học tập" → laptop
            - Communication: "liên lạc", "gọi điện" → phone
            - Entertainment: "giải trí", "entertainment" (general) → phone
            - Gaming context: "play game", "gaming", "chơi game", "game", "gaming device" → null (ambiguous - let agent ask)
            - Fitness: "tập thể dục", "fitness", "health tracking" → watch  
            - Outdoor: "đi cắm trại", "camping", "hiking", "adventure" → camping gear
            
            ⚠️ EXAMPLES of PRIORITY LOGIC:
            - "máy ảnh để đi cắm trại" → camera (direct mention wins over context)
            - "laptop để chụp hình" → laptop (direct mention wins over context)
            - "mua điện thoại để đi học" → phone (direct mention wins over context)
            - "đi cắm trại" → camping gear (no direct mention, use context)
            - "chụp hình đẹp" → camera (no direct mention, use context)
            
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search (PRIORITY: direct product mentioned, then context)",
                "product_name": "specific product name if mentioned, otherwise null",
                "product_description": "specific product features, specifications, or descriptions mentioned, otherwise null",
                "filters": {{
                    "category": "PRIORITY: direct product mentioned, then context mapping - ONLY one of: phone, camera, laptop, watch, camping gear",
                    "min_price": number or null,
                    "max_price": number or null,
                    "min_rating": number or null,
                    "min_discount": number or null
                }}
            }}
            
            EXAMPLES:
            - "máy ảnh để đi cắm trại" → {{"search_query": "camera", "filters": {{"category": "camera"}}}}
            - "laptop để chụp hình" → {{"search_query": "laptop", "filters": {{"category": "laptop"}}}}
            - "đi cắm trại cần gì" → {{"search_query": "camping gear", "filters": {{"category": "camping gear"}}}}
            - "chụp hình đẹp" → {{"search_query": "camera", "filters": {{"category": "camera"}}}}
            
            User input: "{user_input}"
            Return only the JSON object, no additional text.
            """
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL_ID"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts product search intent from user queries. ONLY recognize these 5 product categories: phone, camera, laptop, watch, camping gear. Ignore any other categories."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            result = response.choices[0].message.content.strip()
            try:
                search_intent = json.loads(result)
                if "product_name" not in search_intent:
                    search_intent["product_name"] = None
                if "product_description" not in search_intent:
                    search_intent["product_description"] = None
                if "filters" not in search_intent:
                    search_intent["filters"] = {}
                return search_intent
            except json.JSONDecodeError:
                return {"search_query": user_input, "product_name": None, "product_description": None, "filters": {}}
        except Exception as e:
            print(f"Error extracting search intent: {str(e)}")
            return {"search_query": user_input, "product_name": None, "product_description": None, "filters": {}}

    def _apply_metadata_filters(self, filters: Dict[str, Any]) -> Dict[str, Any] | None:
        clauses: list[dict] = []
        
        # Valid categories only
        if (min_p := filters.get("min_price")) is not None:
            clauses.append({"price": {"$gte": float(min_p)}})
        if (max_p := filters.get("max_price")) is not None:
            clauses.append({"price": {"$lte": float(max_p)}})
        if (min_r := filters.get("min_rating")) is not None:
            clauses.append({"rating": {"$gte": float(min_r)}})
        if (min_d := filters.get("min_discount")) is not None:
            clauses.append({"discount": {"$gte": float(min_d)}})
        if (brand := filters.get("brand")) is not None:
            clauses.append({"brand": {"$eq": str(brand)}})
       
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    def semantic_search(self, user_input: str, limit: int = 10, lang: str = "en", searchFromTool:str = "find_products") -> Dict[str, Any]:
        try:
            search_intent = self.extract_search_intent(user_input)
            product_name = search_intent.get("product_name", None)
            print(f"Product name: {product_name}")
            filters = search_intent.get("filters", {})
            product_category = filters.get("category", None)
            product_description = search_intent.get("product_description", None)
            search_query = search_intent.get("search_query", user_input)
            
            # Construct embedding input: prioritize original search query, enhanced with extracted info
            embedding_parts = []
            
            # Always include the original search query for brand/specific terms
            if search_query and search_query.strip():
                embedding_parts.append(search_query.strip())
            
            # Add category if detected and different from search query
            if product_category and product_category not in search_query.lower():
                embedding_parts.append(product_category)
            
            # Add product name if specifically mentioned
            if product_name:
                embedding_parts.append(product_name)
            
            # Add product description if available
            if product_description:
                embedding_parts.append(product_description)
            
            embedding_input = " ".join(embedding_parts)

            print(f"Search intent extracted: {search_intent}")
            print(f"Original query: {user_input}")
            print(f"Processed search_query: {embedding_input}")

            query_embedding = self.get_embedding(embedding_input)
            if not query_embedding:
                return {"status": "error", "message": "Failed to create query embedding"}

            # STEP 1: Semantic search first (without price filters) - get more results for better filtering
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": min(50, limit * 5),  # Get 5x more results for better filtering
                "include": ["metadatas", "documents", "distances"]
            }
            # Only apply category filter in ChromaDB, NOT price filters
            if filters.get("category"):
                # Title case category to match database format (e.g., "camping gear" -> "Camping Gear")
                category_value = filters.get("category").title()
                search_params["where"] = {"category": {"$eq": category_value}}
                
            results = self.collection.query(**search_params)

            products = []
            valid_categories = ["phone", "camera", "laptop", "watch", "camping gear"]
            
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    # Only include products from valid categories
                    if metadata["category"].lower() not in valid_categories:
                        continue
                        
                    # For cosine distance: distance ranges from 0 (identical) to 2 (opposite)
                    # Convert to similarity: similarity = 1 - (distance / 2) to get range [0, 1]
                    distance = results["distances"][0][i]
                    similarity_score = 1 - (distance / 2)  # Normalize to [0, 1] range
                    
                    # Lower threshold since we're now getting proper similarity scores
                    if similarity_score > 0.3:  # Much lower threshold for better results
                        product_data = {
                            "id": metadata["id"],  # Keep as string, don't convert to int
                            "name": metadata["name"],
                            "category": metadata["category"],
                            "price": metadata["price"],
                            "original_price": metadata["original_price"],
                            "rating": metadata["rating"],
                            "discount": metadata["discount"],
                            "imageUrl": metadata["imageUrl"],
                            "similarity_score": similarity_score,
                            "rec_source": RecommendationSourceEnum.PRODUCT if searchFromTool == "find_products" else (RecommendationSourceEnum.GIFT if searchFromTool == "find_gifts" else None)
                        }
                        products.append(product_data)
                        
            # STEP 2: Apply additional filters (price, rating, etc.) after semantic search
            filtered_products = []
            for product in products:
                # Apply price filters
                if filters.get("min_price") and product["price"] < filters["min_price"]:
                    continue
                if filters.get("max_price") and product["price"] > filters["max_price"]:
                    continue
                # Apply rating filters  
                if filters.get("min_rating") and product["rating"] < filters["min_rating"]:
                    continue
                # Apply discount filters
                if filters.get("min_discount") and product["discount"] < filters["min_discount"]:
                    continue
                    
                filtered_products.append(product)
            
            # STEP 3: Enhanced relevance scoring - brands, categories, and camping gear
            def get_relevance_score(product, search_terms, all_products_names):
                """Calculate relevance score for a product based on search terms"""
                product_name = product["name"].lower()
                product_category = product.get("category", "").lower()
                search_lower = search_terms.lower()
                
                # Extract potential terms from search 
                search_words = search_lower.split()
                
                relevance_score = 0
                
                # Method 1: Category relevance (for camping gear, etc.)
                category_keywords = {
                    "camping gear": ["camping", "tent", "outdoor", "hiking", "backpack", "sleeping", "camp", "coleman"],
                    "phone": ["phone", "smartphone", "mobile", "iphone", "android"],
                    "laptop": ["laptop", "notebook", "computer", "macbook", "gaming"],
                    "camera": ["camera", "dslr", "mirrorless", "lens", "photography"],
                    "watch": ["watch", "smartwatch", "fitness", "tracker"]
                }
                
                # Check for category matches
                for category, keywords in category_keywords.items():
                    if category in product_category:
                        for keyword in keywords:
                            if keyword in search_lower:
                                if category == "camping gear":
                                    relevance_score += 20  # Extra high bonus for camping gear
                                    print(f"Camping gear match: {product_name} - {keyword} (+20)")
                                else:
                                    relevance_score += 15  # High bonus for other categories
                                    print(f"Category match: {product_name} - {keyword} in {category} (+15)")
                                break
                
                # Method 2: Brand relevance (existing logic)
                for word in search_words:
                    if len(word) > 2:  # Skip short words like "of", "in", etc.
                        if word in product_name:
                            relevance_score += 5  # Bonus for word match in product name
                
                # Method 3: Extract brands from product names
                brand_keywords = set()
                for prod_name in all_products_names:
                    # Extract first word (often the brand) from product names
                    first_word = prod_name.split()[0].lower()
                    if len(first_word) > 2:
                        brand_keywords.add(first_word)
                
                # Additional common brands (fallback)
                common_brands = {"samsung", "apple", "iphone", "xiaomi", "google", "pixel", "oneplus", 
                               "sony", "canon", "nikon", "dell", "hp", "lenovo", "macbook", "asus", 
                               "acer", "garmin", "fitbit", "coleman", "huawei", "oppo", "vivo", "lg",
                               "motorola", "realme", "nothing", "honor"}
                brand_keywords.update(common_brands)
                
                # Check for brand matches
                for brand in brand_keywords:
                    if brand in search_lower:
                        if brand in product_name:
                            relevance_score += 10  # High score for exact brand match
                            print(f"Brand match: {product_name} - {brand} (+10)")
                        else:
                            relevance_score -= 1   # Small penalty if search mentions brand but product doesn't have it
                
                # Method 4: Special camping gear detection
                camping_terms = ["tent", "sleeping bag", "backpack", "camping", "outdoor", "hiking", 
                               "coleman", "camp", "portable", "waterproof", "outdoor gear", "survival"]
                if any(term in search_lower for term in camping_terms):
                    if "camping gear" in product_category:
                        relevance_score += 25  # Maximum bonus for camping gear category match
                        print(f"Strong camping gear match: {product_name} (+25)")
                    elif any(term in product_name for term in camping_terms):
                        relevance_score += 15  # Bonus for camping-related product name
                        print(f"Camping term in name: {product_name} (+15)")
                
                return relevance_score
            
            # Sort filtered products by relevance + similarity score
            search_terms = user_input + " " + (search_query or "")
            all_product_names = [p["name"] for p in filtered_products]
            
            for product in filtered_products:
                relevance_score = get_relevance_score(product, search_terms, all_product_names)
                # Combine relevance with similarity score - increase weight for camping gear
                if product.get("category", "").lower() == "camping gear":
                    product["final_score"] = product["similarity_score"] + (relevance_score * 0.15)  # Higher weight for camping gear
                else:
                    product["final_score"] = product["similarity_score"] + (relevance_score * 0.1)   # Standard weight
            
            # Sort by final score (brand relevance + similarity)
            filtered_products.sort(key=lambda x: x.get("final_score", x.get("similarity_score", 0)), reverse=True)
                
            # Limit results to requested amount
            products = filtered_products[:limit]
            
            print(f"DEBUG: Semantic search found {len(results['metadatas'][0] if results['metadatas'] else [])} total")
            print(f"DEBUG: After similarity filter: {len(products)} products") 
            print(f"DEBUG: After price/rating filters: {len(filtered_products)} products")
            print(f"DEBUG: Final result (limited to {limit}): {len(products)} products")

            # Analyze product relevance for better messaging
            def analyze_search_results(user_input: str, products: List[Dict]) -> Dict[str, Any]:
                """Analyze search results to categorize exact matches vs related products"""
                search_words = user_input.lower().split()
                brand_terms = {"samsung", "apple", "iphone", "xiaomi", "sony", "huawei", "lg", "google", "oneplus"}
                
                exact_matches = []
                related_products = []
                
                # Check if user searched for a specific brand
                searched_brands = [word for word in search_words if word in brand_terms]
                
                for product in products:
                    product_name = product.get("name", "").lower()
                    is_exact_match = False
                    
                    # Check if product matches the searched brand
                    if searched_brands:
                        for brand in searched_brands:
                            if brand in product_name:
                                is_exact_match = True
                                break
                    else:
                        # If no specific brand searched, consider high-score products as exact matches
                        if product.get("final_score", 0) > product.get("similarity_score", 0) + 0.5:
                            is_exact_match = True
                    
                    if is_exact_match:
                        exact_matches.append(product)
                    else:
                        related_products.append(product)
                
                return {
                    "exact_matches": exact_matches,
                    "related_products": related_products,
                    "searched_brands": searched_brands
                }
            
            # Analyze results before creating response
            result_analysis = analyze_search_results(user_input, products)
            
            # Check if AI automatically chose a category (when search_query != user_input)
            auto_chosen_category = None
            if search_query and search_query.lower() != user_input.lower() and search_query in ["phone", "camera", "laptop", "watch", "camping gear"]:
                auto_chosen_category = search_query
            
            # STEP 4: Product Relationship Logic - Check for complementary product queries
            if self.relationship_service:
                try:
                    relationship_context = self.relationship_service.detect_relationship_query(user_input)
                    if relationship_context:
                        print(f"DEBUG: Detected relationship query - Context: {relationship_context}")
                        
                        # Get relationship suggestions
                        suggestions = self.relationship_service.get_smart_suggestions(user_input, [])
                        
                        if suggestions and suggestions.get("suggestions"):
                            # Mix original results with relationship suggestions
                            relationship_products = []
                            
                            for suggestion in suggestions["suggestions"][:3]:  # Top 3 suggestions
                                # Search for products in suggested category
                                suggested_category = suggestion["category"]
                                category_result = self.semantic_search(suggested_category, 2, lang, searchFromTool)
                                
                                if category_result["status"] == "success" and category_result["products"]:
                                    for rel_product in category_result["products"]:
                                        rel_product["relationship_reason"] = suggestion["reason"]
                                        rel_product["relationship_type"] = suggestion["relationship"] 
                                        rel_product["from_relationship"] = True
                                        relationship_products.append(rel_product)
                            
                            # If we have relationship products, prioritize them
                            if relationship_products:
                                # Combine: relationship products first, then original products
                                combined_products = relationship_products[:limit//2] + products[:limit//2]
                                products = combined_products[:limit]
                                
                                # Update auto_chosen_category for better messaging
                                if not auto_chosen_category:
                                    auto_chosen_category = f"relationship_{relationship_context}"
                                    
                                print(f"DEBUG: Enhanced results with {len(relationship_products)} relationship products")
                
                except Exception as e:
                    print(f"DEBUG: Error in relationship logic: {e}")
                    # Continue with original products if relationship service fails
            
            composed_response = self.make_intro_sentence(user_input, products, lang, result_analysis, auto_chosen_category, displayed_count=3)
            print(f"DEBUG: Composed response: {composed_response}")

            return {
                "status": "success",
                "search_intent": search_intent,
                "intro": composed_response["intro"],
                "header": composed_response["header"],
                "products": products,  # Use the original products list
                "show_all_product": composed_response["show_all_product"],
                "total_results": len(products)
            }
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return {"status": "error", "message": f"Search error: {str(e)}"}

    async def voice_search(self, audio_file) -> Dict[str, Any]:
        try:
            transcription_result = self.transcribe_audio(audio_file)
            if transcription_result["status"] != "success":
                return transcription_result
            
            transcribed_text = transcription_result["text"]
            
            # Use semantic_search_middleware instead of semantic_search for consistency
            messages = [{"role": "user", "content": transcribed_text}]
            search_result = await self.semantic_search_middleware(messages)
            print(f"DEBUG: Search result from voice search: {search_result}")
            
            # Update response structure to match text search format
            if isinstance(search_result, dict) and search_result.get("status") == "success":
                # Add voice-specific metadata while preserving the structured response
                search_result["transcribed_text"] = transcribed_text
                search_result["original_query_type"] = "voice"
                
                # Ensure all required fields are present for consistency with text search
                if "intro" not in search_result:
                    search_result["intro"] = ""
                if "header" not in search_result:
                    search_result["header"] = ""
                if "function_used" not in search_result:
                    search_result["function_used"] = None
                if "language_detected" not in search_result:
                    search_result["language_detected"] = self.USER_LANG_CODE
                if "messages" not in search_result:
                    search_result["messages"] = messages
            
            return search_result
        except Exception as e:
            print(f"Error in voice search: {str(e)}")
            return {"status": "error", "message": f"Voice search error: {str(e)}"}

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            count = self.collection.count()
            return {"status": "success", "collection_name": self.collection_name, "total_products": count, "embedding_model": self.embedding_model}
        except Exception as e:
            return {"status": "error", "message": f"Error getting stats: {str(e)}"}

    def detect_language(self, text: str) -> str:
        if not self.openai_available:
            return "en"
        try:
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL_ID"),
                messages=[
                    {"role": "system", "content": "Detect the language of the following text. Return only the language code (en, vi, fr, es, etc.)."},
                    {"role": "user", "content": text}
                ],
                temperature=0,
                max_tokens=10
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"Error detecting language: {str(e)}")
            return "en"

    # ---------- Copy helpers ----------

    def make_intro_sentence(self, user_input: str, products: List[Dict], lang_code: str, result_analysis: Dict[str, Any] = None, auto_chosen_category: str = None, displayed_count: int = 3) -> Dict[str, str]:
        try:
            product_count = len(products)
            remaining_count = max(0, product_count - displayed_count)
            
            # Extract analysis data
            if result_analysis:
                exact_matches = len(result_analysis.get("exact_matches", []))
                related_products = len(result_analysis.get("related_products", []))
                searched_brands = result_analysis.get("searched_brands", [])
            else:
                exact_matches = product_count
                related_products = 0
                searched_brands = []
            
            # Create context for more intelligent messaging
            context_info = ""
            if searched_brands and exact_matches > 0:
                brand_name = searched_brands[0].title()
                if exact_matches == product_count:
                    context_info = f"All {product_count} products are {brand_name} products."
                else:
                    context_info = f"Found {exact_matches} {brand_name} products and {related_products} similar/related products in the same category."
            elif exact_matches < product_count:
                context_info = f"Found {exact_matches} exact matches and {related_products} related products."
            
            # Add auto-chosen category context
            if auto_chosen_category:
                if context_info:
                    context_info += f" AI automatically selected {auto_chosen_category} category for this query."
                else:
                    context_info = f"AI automatically selected {auto_chosen_category} category for this query."
            
            # Enhanced prompt with result analysis
            use_case_hint = ""
            if displayed_count == 1 and products:
                product_name = products[0].get('name', '')
                if any(keyword in user_input.lower() for keyword in ['lập trình', 'programming', 'coding', 'code', 'dev']):
                    use_case_hint = f"IMPORTANT: Explain why {product_name} is excellent for programming/coding work in the intro."
                elif any(keyword in user_input.lower() for keyword in ['gaming', 'game', 'chơi game']):
                    use_case_hint = f"IMPORTANT: Explain why {product_name} is great for gaming in the intro."
                elif any(keyword in user_input.lower() for keyword in ['creative', 'design', 'photo', 'video']):
                    use_case_hint = f"IMPORTANT: Explain why {product_name} is perfect for creative work in the intro."
                elif displayed_count == 1:
                    use_case_hint = f"IMPORTANT: Briefly explain why {product_name} is the best choice in the intro."

            prompt = f"""
            You are a multilingual e-commerce assistant. Generate a JSON response with exactly these 3 fields for a product search result.

            USER SEARCH: "{user_input}"
            TOTAL PRODUCTS: {product_count}
            DISPLAYED PRODUCTS: {displayed_count}
            REMAINING PRODUCTS: {remaining_count}
            EXACT MATCHES: {exact_matches}
            RELATED PRODUCTS: {related_products}
            CONTEXT: {context_info}
            AUTO_CHOSEN_CATEGORY: {auto_chosen_category or "None"}
            LANGUAGE CODE: {lang_code}
            {use_case_hint}

            Generate response in the language indicated by the language code ({lang_code}).

            Return ONLY a valid JSON object with these exact keys:
            {{
                "intro": "A warm, encouraging 1-sentence introduction about the search results (max 30 words). Be cheerful and specific about what was found. IMPORTANT: If AUTO_CHOSEN_CATEGORY is not None, mention that you've selected this category for the user in the intro.",
                "header": "A short subtitle introducing the product list below (max 15 words). Be natural and friendly.",
                "show_all_product": "IMPORTANT: Create a VARIED, NATURAL question asking if the user wants to see the remaining {remaining_count} products. MUST use the exact REMAINING PRODUCTS count ({remaining_count}). Use different phrasings each time - be creative and natural. MUST end with a question mark. Only generate if remaining_count > 0, otherwise empty string."
            }}

            Guidelines:
            - Be specific about exact matches vs related products
            - If searching for a brand, mention the brand in intro
            - If AUTO_CHOSEN_CATEGORY is provided, mention it naturally in intro (e.g., "I've selected camera products for you" or "Here are some phone options I picked")
            - For show_all_product: MUST use the exact remaining count ({remaining_count}) - do not use other numbers
            - Always include question about viewing the remaining {remaining_count} products with this EXACT number
            - Keep it natural and helpful
            - If remaining_count <= 0: return empty string for show_all_product
            - Language consistency: Use the specified language code throughout

            AUTO_CHOSEN_CATEGORY Examples:
            
            English:
            - "I've selected phone products for you - found {product_count} great options!"
            - "Based on your query, here are {product_count} camera recommendations!"
            - "I picked laptop items for you - discovered {product_count} excellent choices!"
            
            Vietnamese:
            - "Tôi đã chọn điện thoại cho bạn - tìm được {product_count} lựa chọn tuyệt vời!"
            - "Dựa trên yêu cầu của bạn, đây là {product_count} sản phẩm camera hay ho!"
            - "Tôi đã chọn laptop - khám phá {product_count} sản phẩm xuất sắc!"

            IMPORTANT: For show_all_product, ALWAYS use the exact remaining count ({remaining_count}). Examples of varied phrasing (MUST use {remaining_count}):
            
            English variations (use exact number {remaining_count}):
            - "Want to explore {remaining_count} more similar options?"
            - "Curious about {remaining_count} other related products?"
            - "Shall I show you {remaining_count} additional recommendations?"
            - "Interested in checking out {remaining_count} more alternatives?"
            - "Would you like to discover {remaining_count} other great choices?"
            - "How about browsing {remaining_count} more related items?"
            
            Vietnamese variations (use exact number {remaining_count}):
            - "Muốn khám phá thêm {remaining_count} sản phẩm tương tự không?"
            - "Bạn có tò mò về {remaining_count} sản phẩm khác không?"
            - "Có muốn xem {remaining_count} gợi ý khác không?"
            - "Thích tìm hiểu {remaining_count} lựa chọn khác không?"
            - "Muốn khám phá {remaining_count} sản phẩm hay ho khác không?"
            - "Có muốn duyệt qua {remaining_count} sản phẩm liên quan khác?"
            - "Bạn muốn xem thêm {remaining_count} lựa chọn thú vị không?"

            BE CREATIVE - use different verbs, adjectives, and structures while keeping the core meaning and EXACT remaining count ({remaining_count})!

            Return only the JSON object, no other text.
            """
            
            response = self.llm.invoke(prompt).content.strip()
            
            # Parse the JSON response
            try:
                result = json.loads(response)
                return {
                    "intro": result.get("intro", ""),
                    "header": result.get("header", ""),
                    "show_all_product": result.get("show_all_product", "")
                }
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                try:
                    if '```json' in response:
                        json_start = response.find('```json') + 7
                        json_end = response.find('```', json_start)
                        json_content = response[json_start:json_end].strip()
                        result = json.loads(json_content)
                        return {
                            "intro": result.get("intro", ""),
                            "header": result.get("header", ""),
                            "show_all_product": result.get("show_all_product", "")
                        }
                    else:
                        raise e
                except (json.JSONDecodeError, ValueError) as e2:
                    print(f"Failed to parse LLM JSON response: {e}")
                    print(f"Raw response: {response}")
                    raise Exception("LLM returned invalid JSON")
            
        except Exception as e:
            print(f"Error in make_response_sentence: {str(e)}")
            # Fallback to static messages
            fallback_intros = {
                "en": [
                    f"I found {len(products)} products for your search!",
                    f"Discovered {len(products)} great options for you!",
                    f"Here are {len(products)} products that match your needs!",
                    f"Found {len(products)} interesting products!",
                    f"Located {len(products)} products you might like!"
                ][hash(user_input + "intro") % 5] if products else "Sorry, no products found for your search.",
                "vi": [
                    f"Tôi tìm thấy {len(products)} sản phẩm cho bạn!",
                    f"Khám phá được {len(products)} lựa chọn tuyệt vời!",
                    f"Đây là {len(products)} sản phẩm phù hợp với bạn!",
                    f"Tìm được {len(products)} sản phẩm thú vị!",
                    f"Phát hiện {len(products)} sản phẩm bạn có thể thích!"
                ][hash(user_input + "intro") % 5] if products else "Xin lỗi, không tìm thấy sản phẩm nào.",
                "ko": [
                    f"검색에서 {len(products)}개 제품을 찾았습니다!",
                    f"{len(products)}개의 좋은 옵션을 발견했어요!",
                    f"당신에게 맞는 {len(products)}개 제품이 있습니다!",
                    f"{len(products)}개의 흥미로운 제품을 찾았어요!",
                    f"마음에 들 만한 {len(products)}개 제품을 찾았습니다!"
                ][hash(user_input + "intro") % 5] if products else "죄송합니다. 제품을 찾을 수 없습니다.",
                "ja": [
                    f"検索で{len(products)}個の商品を見つけました！",
                    f"{len(products)}個の素晴らしい選択肢を発見しました！",
                    f"あなたにぴったりの{len(products)}個の商品があります！",
                    f"{len(products)}個の興味深い商品を見つけました！",
                    f"お気に入りになりそうな{len(products)}個の商品を見つけました！"
                ][hash(user_input + "intro") % 5] if products else "申し訳ございませんが、商品が見つかりませんでした。"
            }
            
            fallback_headers = {
                "en": [
                    "Here are your product suggestions:",
                    "Check out these recommendations:",
                    "Take a look at these options:",
                    "Here's what I found for you:",
                    "These products might interest you:"
                ][hash(user_input + "header") % 5],
                "vi": [
                    "Đây là những sản phẩm gợi ý cho bạn:",
                    "Hãy xem những gợi ý này:",
                    "Cùng khám phá những lựa chọn sau:",
                    "Đây là những gì tôi tìm được cho bạn:",
                    "Những sản phẩm này có thể phù hợp với bạn:"
                ][hash(user_input + "header") % 5],
                "ko": [
                    "제품 추천 목록입니다:",
                    "이런 추천 상품들을 확인해보세요:",
                    "다음 옵션들을 살펴보세요:",
                    "당신을 위해 찾은 제품들입니다:",
                    "관심 가질 만한 제품들입니다:"
                ][hash(user_input + "header") % 5],
                "ja": [
                    "おすすめ商品一覧：",
                    "こちらの推薦商品をご確認ください：",
                    "以下のオプションをご覧ください：",
                    "あなたのために見つけた商品です：",
                    "興味を持てそうな商品はこちら："
                ][hash(user_input + "header") % 5]
            }
            
            fallback_show_all = {
                "en": [
                    f"Want to explore {remaining_count} more similar options?",
                    f"Curious about {remaining_count} other related products?", 
                    f"Shall I show you {remaining_count} additional recommendations?",
                    f"Interested in checking out {remaining_count} more alternatives?",
                    f"How about browsing {remaining_count} more related items?"
                ][hash(user_input) % 5] if remaining_count > 0 else "",
                "vi": [
                    f"Bạn có muốn xem hết {len(products)} sản phẩm không?",
                    f"Có muốn khám phá tất cả {len(products)} lựa chọn không?",
                    f"Bạn có tò mò về toàn bộ {len(products)} sản phẩm không?", 
                    f"Muốn xem đầy đủ {len(products)} gợi ý không?",
                    f"Có muốn duyệt qua cả {len(products)} sản phẩm không?"
                ][hash(user_input) % 5] if remaining_count > 0 else "",
                "ko": [
                    f"{remaining_count}개의 유사한 제품을 더 보시겠습니까?",
                    f"{remaining_count}개의 관련 제품이 궁금하신가요?",
                    f"{remaining_count}개의 추가 제품을 확인해보실까요?",
                    f"{remaining_count}개의 대안을 살펴보시겠어요?",
                    f"{remaining_count}개의 관련 아이템을 둘러보실래요?"
                ][hash(user_input) % 5] if remaining_count > 0 else "",
                "ja": [
                    f"{remaining_count}個の類似商品をもっと見ますか？",
                    f"{remaining_count}個の関連商品に興味はありませんか？",
                    f"{remaining_count}個の追加のおすすめを見せましょうか？",
                    f"{remaining_count}個の代替品をチェックしませんか？",
                    f"{remaining_count}個の関連アイテムを閲覧しませんか？"
                ][hash(user_input) % 5] if remaining_count > 0 else ""
            }
            
            return {
                "intro": fallback_intros.get(lang_code, fallback_intros["en"]),
                "header": fallback_headers.get(lang_code, fallback_headers["en"]),
                "show_all_product": fallback_show_all.get(lang_code, fallback_show_all["en"])
            }

    def compose_response(self, intro: str, items, lang_code: str):
        header = self.HEADER_BY_LANG.get(lang_code, self.HEADER_BY_LANG["en"])
        return {"intro": intro, "header": header, "products": items}

    def _get_external_gift_products(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Get products from external gift recommendations with labels assigned to showLabel.
        
        Returns:
            List of product dictionaries with showLabel field
        """
        try:
            # Get external gift recommendations
            gift_recommendations = self.middleware_service.find_gifts_external(user_input, 10)
            print(f"DEBUG _get_external_gift_products - external recommendations: {gift_recommendations}")
            
            external_products = []
            for recommendation in gift_recommendations:
                label = recommendation.get("label")
                product_ids = recommendation.get("product_ids", [])
                
                for product_id in product_ids:
                    product_data = self.product_service.get_product_by_id(product_id)
                    if product_data:
                        # Create product structure similar to semantic_search results
                        external_product = {
                            "id": str(product_id),
                            "name": product_data.get("name", ""),
                            "category": product_data.get("category", ""),
                            "price": product_data.get("price", 0),
                            "original_price": product_data.get("original_price", product_data.get("price", 0)),
                            "rating": product_data.get("rating", 0),
                            "discount": product_data.get("discount", 0),
                            "imageUrl": product_data.get("imageUrl", ""),
                            "similarity_score": 1.0,  # High score for external recommendations
                            "rec_source": ALGORITHM_TO_REC_SOURCE.get(label, RecommendationSourceEnum.GIFT.value)  # Map algorithm label to rec_source enum
                        }
                        external_products.append(external_product)
            
            print(f"DEBUG _get_external_gift_products - external products with labels: {external_products}")
            return external_products
            
        except Exception as e:
            print(f"Error getting external gift products: {str(e)}")
            return []


    def truncate_conversation_history(self, messages: List[Dict[str, str]], max_messages: int = 25) -> List[Dict[str, str]]:
        """Keep system message + last N conversation messages to prevent token overflow"""
        
        if len(messages) <= max_messages + 1:  # +1 for system message
            return messages
        
        # Separate system and conversation messages
        system_msg = None
        conversation_msgs = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg
            else:
                conversation_msgs.append(msg)
        
        # Keep more recent conversation messages for better context
        recent_conversation = conversation_msgs[-max_messages:]
        
        # Combine: system + recent conversation
        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(recent_conversation)
        
        print(f"DEBUG: Truncated messages from {len(messages)} to {len(result)} (system + {len(recent_conversation)} conversation)")
        return result

    # ---------- Chat middleware ----------
    async def semantic_search_middleware(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Truncate conversation history to prevent token overflow (keep more context)
        messages = self.truncate_conversation_history(messages, max_messages=25)
        
        # last user input
        user_input = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        # update language ON INSTANCE
        self.USER_LANG_CODE = self.detect_language(user_input)

        # ensure system message is always present with updated instructions
        agent_messages = messages.copy()
        if not agent_messages or agent_messages[0].get("role") != "system":
            agent_messages.insert(0, {"role": "system", "content": SYSTEM_INSTRUCTIONS})
        else:
            # Update existing system message with latest instructions
            agent_messages[0]["content"] = SYSTEM_INSTRUCTIONS

        print(f"DEBUG: User input: {user_input}")
        print(f"DEBUG: Language detected: {self.USER_LANG_CODE}")
        print(f"DEBUG: Messages count after truncation: {len(agent_messages)}")

        # allow more steps for tool calling
        response = self.agent.invoke({"messages": agent_messages}, config={"recursion_limit": 5})
        print(f"DEBUG: Full agent response: {response}")

        msgs = response["messages"]
        tool_msgs = [m for m in msgs if isinstance(m, ToolMessage) and getattr(m, "name", None) in self.TOOL_NAMES]

        ai_response = tool_msgs[-1].content if tool_msgs else msgs[-1].content
        print(f"DEBUG: Final AI response (raw): {ai_response}")

        # parse JSON if tool returned JSON string
        try:
            ai_response_data = json.loads(ai_response) if isinstance(ai_response, str) else ai_response
            print(f"DEBUG: Successfully parsed JSON: {ai_response_data}")
            
            # Save products to context if this was a find_products call
            if tool_msgs and tool_msgs[-1].name == "find_products" and ai_response_data.get("products"):
                self._context_products = ai_response_data["products"]
                print(f"DEBUG: Saved {len(self._context_products)} products to context for analysis")
                
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse JSON: {e}")
            print(f"DEBUG: This is a text response (clarification), not JSON")
            # This is not an error - it's a text response from agent (like clarification questions)
            ai_response_data = {
                "status": "success",
                "intro": ai_response,  # Use the actual AI response as intro
                "header": "",
                "products": [],
                "total_results": 0,
                "is_text_response": True  # Flag to indicate this is a direct text response
            }

        messages.append({"role": "assistant", "content": ai_response})

        # If it's a text response (clarification, etc.), return it directly
        if ai_response_data.get("is_text_response"):
            print(f"DEBUG: Returning text response with intro: {ai_response}")
            return {
                "status": "success",
                "function_used": None,
                "language_detected": self.USER_LANG_CODE,
                "search_intent": None,
                "intro": ai_response,
                "header": "",
                "products": [],
                "total_results": 0,
                "messages": messages,
                "is_clarification": True
            }

        print(f"DEBUG: Returning tool response")
        
        return {
            "status": ai_response_data.get("status", "success"),
            "function_used": tool_msgs[-1].name if tool_msgs else None,
            "language_detected": self.USER_LANG_CODE,
            "search_intent": ai_response_data.get("search_intent"),
            "intro": ai_response_data.get("intro"),
            "header": ai_response_data.get("header"),
            "products": ai_response_data.get("products", []),
            "show_all_product": ai_response_data.get("show_all_product"),  # Add missing show_all_product field
            "total_results": ai_response_data.get("total_results", 0),
            "messages": messages,
        }
