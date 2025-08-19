import os
import json
import asyncio
import string
import sys
import tempfile
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
import chromadb
from chromadb.config import Settings
import numpy as np
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from utils.product_keywords import get_product_keywords_from_dict

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

from models import Product
from product_service import ProductService

# Load environment variables
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path)

# System instructions for the AI agent
SYSTEM_INSTRUCTIONS = """
You are a shopping assistant that helps users find products in 5 categories: phone, camera, laptop, watch, camping gear.

CORE BEHAVIOR:
1. For gift requests without specific category: Ask user to choose a category before calling tools
2. For gift requests with category: Call find_gifts tool 
3. For general product searches: Call find_products tool
4. For invalid categories: Explain limitations and suggest valid alternatives

GIFT HANDLING LOGIC:
- If user mentions recipients (mom, dad, friend, etc.) or gift occasions BUT doesn't specify a product category:
  → ASK: "What type of gift are you looking for? I can help with: phone, camera, laptop, watch, or camping gear"
- If user mentions recipients AND specifies a valid category:
  → CALL: find_gifts tool with the category
- If user specifies category after gift context:
  → CALL: find_gifts tool (maintain gift context)

GENERAL PRODUCT LOGIC:
- If user asks for products without gift context:
  → CALL: find_products tool directly

CATEGORY RESTRICTIONS:
- ONLY these 5 categories: phone, camera, laptop, watch, camping gear
- For invalid categories (clothes, jewelry, furniture, etc.):
  → EXPLAIN: "I only help with phone, camera, laptop, watch, and camping gear"
  → SUGGEST: alternatives within valid categories

REPEATED QUERIES:
- If user repeats same query (e.g., "phone" then "phone" again): ALWAYS call the appropriate tool again
- Each query should trigger fresh tool execution regardless of conversation history
- MAINTAIN CONTEXT: If gift context was established earlier, continue using find_gifts for repeated queries

EXAMPLES:
✅ "I want gift for mom" → ASK for category first
✅ "Gift for mom - phone" → Call find_gifts("phone", recipient="mom")  
✅ "Phone for mom" → Call find_gifts("phone", recipient="mom")
✅ "Phone" (no gift context) → Call find_products("phone")
✅ User: "gift for dad" → You: "What category?" → User: "laptop" → Call find_gifts("laptop", recipient="dad")
✅ If gift context exists and user says "phone" again → Call find_gifts("phone", maintain context)
❌ "Clothes for mom" → Explain limitations, suggest "watch for fashion accessory"

CONVERSATION FLOW:
- Always check if gift context exists in conversation history
- If gift context exists and user mentions category → use find_gifts (maintain gift context)
- If gift context exists but no category → ask for category
- If no gift context → use find_products

Remember: ASK before calling tools when gift context exists but category is unclear.
"""

class AIService:
    def __init__(self):
        # ---- Basic setup
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required but not available. Please install with: pip install chromadb")
        
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
            """Find and recommend products based on user's shopping needs. Only searches in: phone, camera, laptop, watch, camping gear categories."""
            
            # Return JSON-encoded string for consistent downstream parsing
            result = self.semantic_search(query, 10, self.USER_LANG_CODE)
            return json.dumps(result, ensure_ascii=False)

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
            
            # Use the category for search
            result = self.semantic_search(category, 5, self.USER_LANG_CODE)
            result["recipient"] = recipient
            result["requested_category"] = category
            result["occasion"] = occasion
            
            # Update the intro message to be gift-specific
            if "intro" in result:
                result["intro"] = f"Here are some wonderful {category} gifts for {recipient} - {result['intro']}"
            
            return json.dumps(result, ensure_ascii=False)

        self.available_tools = [find_products, find_gifts]
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
                metadata={"hnsw:space": "cosine"}
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
    
    def _get_llm_keywords(self, product: Product) -> List[str]:
        """Generate keywords using LLM for any product category"""
        if not self.openai_available:
            return []
        
        try:
            prompt = f"""Generate 15-20 relevant search keywords for this product:
            
            Product Name: {product.name}
            Category: {product.category}
            Description: {product.description or 'No description'}
            
            Include:
            - Synonyms for the product name and category
            - Common search terms people would use
            - Related terms and use cases
            - Brand alternatives and variations
            - Technical terms and specifications
            
            Return only comma-separated keywords, no explanations.
            
            Examples:
            
            For a lamp:
            lamp, light, lighting, illumination, table lamp, desk lamp, floor lamp, ceiling lamp, bulb, brightness, led lamp, smart lamp, work lamp, reading lamp, ambient light
            
            For a speaker:
            speaker, audio, sound, music, wireless speaker, bluetooth speaker, portable speaker, sound system, stereo, audio device, music player, bass, volume, acoustics, sound quality
            
            For a smartphone:
            phone, smartphone, mobile phone, cell phone, iphone, android, mobile device, cellular, handset, telephone, smart phone, mobile, communication device, touchscreen phone, 5g phone
            
            For a laptop:
            laptop, computer, notebook, portable computer, pc, macbook, gaming laptop, work laptop, ultrabook, netbook, computing device, mobile computer, personal computer, workstation
            
            For headphones:
            headphones, earphones, earbuds, audio headset, wireless headphones, bluetooth headphones, noise cancelling headphones, over ear headphones, in ear headphones, music headphones, gaming headset
            """
            
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates search keywords for e-commerce products. Generate comprehensive keywords that customers might use to search for products."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the comma-separated keywords
            keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = []
            for kw in keywords:
                if kw.lower() not in seen:
                    seen.add(kw.lower())
                    unique_keywords.append(kw)
            
            return unique_keywords
            
        except Exception as e:
            print(f"Error generating LLM keywords: {str(e)}")
            return []
    
    def generate_category_keywords(self, categories: List[str]) -> Dict[str, List[str]]:
        """Generate keywords for all categories using LLM based on actual products in each category"""
        if not self.openai_available:
            print("⚠️ OpenAI not available, cannot generate category keywords")
            return {}
        
        try:
            print(f"🤖 Generating product-aware keywords for {len(categories)} categories...")
            category_keywords = {}
            
            # Get all products to analyze
            products_data = self.product_service.get_all_products()
            if not products_data:
                print("⚠️ No products found, falling back to basic category keywords")
                return self._generate_basic_category_keywords(categories)
            
            # Group products by category
            products_by_category = {}
            for product_dict in products_data:
                category = product_dict.get('category', 'Unknown')
                if category not in products_by_category:
                    products_by_category[category] = []
                products_by_category[category].append(product_dict)
            
            for category in categories:
                try:
                    products_in_category = products_by_category.get(category, [])
                    
                    if not products_in_category:
                        print(f"⚠️ No products found for category '{category}', using basic keywords")
                        basic_keywords = self._generate_basic_category_keywords([category])
                        category_keywords[category] = basic_keywords.get(category, [])
                        continue
                    
                    # Extract information from actual products
                    brands = set()
                    product_names = []
                    descriptions = []
                    key_features = set()
                    
                    for product in products_in_category[:10]:  # Limit to first 10 products for analysis
                        # Extract brand from product name (usually first word)
                        name = product.get('name', '')
                        if name:
                            product_names.append(name)
                            # Try to extract brand (first word before space or common patterns)
                            name_parts = name.split()
                            if name_parts:
                                potential_brand = name_parts[0]
                                # Common brand patterns
                                if len(potential_brand) > 2 and potential_brand.isalpha():
                                    brands.add(potential_brand)
                        
                        # Extract description keywords
                        desc = product.get('description', '')
                        if desc:
                            descriptions.append(desc)
                            # Extract key technical terms
                            desc_lower = desc.lower()
                            # Look for technical specs and features
                            tech_terms = ['wireless', 'bluetooth', 'smart', 'led', 'usb', 'hdmi', 'wifi', 'app', 'battery', 'rechargeable', 'portable', 'waterproof', 'noise', 'hd', '4k', 'gaming']
                            for term in tech_terms:
                                if term in desc_lower:
                                    key_features.add(term)
                    
                    # Create comprehensive prompt with actual product data
                    brands_text = ', '.join(list(brands)[:8]) if brands else "various brands"
                    features_text = ', '.join(list(key_features)[:10]) if key_features else "standard features"
                    sample_names = '; '.join(product_names[:5]) if product_names else "no sample names"
                    
                    prompt = f"""Generate 20-25 search keywords for the "{category}" category based on actual products in our inventory.
                    
                    ACTUAL PRODUCT DATA FROM OUR INVENTORY:
                    - Brands we carry: {brands_text}
                    - Key features found: {features_text}
                    - Sample product names: {sample_names}
                    
                    Generate keywords that customers would use to search for these specific products. Include:
                    1. Category terms and synonyms
                    2. ACTUAL brand names from our inventory: {brands_text}
                    3. Technical features found in our products: {features_text}
                    4. Common search variations and use cases
                    5. Alternative names customers might use
                    
                    Focus on keywords that match the ACTUAL products we sell, not generic category terms.
                    
                    Return only comma-separated keywords, no explanations.
                    
                    Examples based on real inventory:
                    
                    For "Speaker" with brands "JBL, Sony" and features "bluetooth, wireless, portable":
                    speaker, JBL speaker, Sony speaker, bluetooth speaker, wireless speaker, portable speaker, audio, sound, music, JBL, Sony, bluetooth audio, wireless audio, portable audio, sound system, stereo, bass, volume, party speaker, outdoor speaker
                    
                    For "Laptop" with brands "Apple, Dell, HP" and features "gaming, business, lightweight":
                    laptop, computer, Apple laptop, Dell laptop, HP laptop, MacBook, gaming laptop, business laptop, notebook, portable computer, Apple, Dell, HP, gaming computer, work laptop, ultrabook, PC, computing device
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that generates search keywords based on actual product inventory data. Focus on real brands and features found in the products."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=300
                    )
                    
                    result = response.choices[0].message.content.strip()
                    
                    # Parse the comma-separated keywords
                    keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_keywords = []
                    for kw in keywords:
                        if kw.lower() not in seen:
                            seen.add(kw.lower())
                            unique_keywords.append(kw)
                    
                    category_keywords[category] = unique_keywords
                    print(f"✅ Generated {len(unique_keywords)} product-aware keywords for '{category}' (analyzed {len(products_in_category)} products, {len(brands)} brands)")
                    
                    # Small delay to respect rate limits
                    import time
                    time.sleep(0.8)
                    
                except Exception as e:
                    print(f"❌ Error generating keywords for category '{category}': {str(e)}")
                    category_keywords[category] = []
            
            return category_keywords
            
        except Exception as e:
            print(f"❌ Error in generate_category_keywords: {str(e)}")
            return {}
    
    def _generate_basic_category_keywords(self, categories: List[str]) -> Dict[str, List[str]]:
        """Fallback method to generate basic category keywords without product analysis"""
        if not self.openai_available:
            return {}
            
        category_keywords = {}
        for category in categories:
            try:
                prompt = f"""Generate 15-20 basic search keywords for the "{category}" category.
                
                Include common terms, synonyms, and typical product types in this category.
                Return only comma-separated keywords, no explanations.
                
                Category: {category}"""
                
                response = self.openai_client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "Generate basic category keywords."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=150
                )
                
                result = response.choices[0].message.content.strip()
                keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
                
                # Remove duplicates
                seen = set()
                unique_keywords = []
                for kw in keywords:
                    if kw.lower() not in seen:
                        seen.add(kw.lower())
                        unique_keywords.append(kw)
                
                category_keywords[category] = unique_keywords
                
            except Exception as e:
                print(f"❌ Error generating basic keywords for '{category}': {str(e)}")
                category_keywords[category] = []
        
        return category_keywords
    
    def should_regenerate_keywords(self, categories: List[str]) -> bool:
        """Check if keywords need to be regenerated based on data changes"""
        try:
            # Check if keywords file exists
            if not os.path.exists("category_keywords.json"):
                print("📄 No keywords file found, need to generate")
                return True
            
            # Load existing keywords data
            with open("category_keywords.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            existing_categories = set(existing_data.get("categories", {}).keys())
            current_categories = set(categories)
            
            # Check if categories changed
            if existing_categories != current_categories:
                print(f"📂 Categories changed: {existing_categories} → {current_categories}")
                return True
            
            # Check if keywords are too old (regenerate weekly)
            from datetime import datetime, timedelta
            try:
                generated_at = datetime.fromisoformat(existing_data.get("generated_at", ""))
                age = datetime.now() - generated_at
                if age > timedelta(days=7):
                    print(f"⏰ Keywords are {age.days} days old, regenerating")
                    return True
            except:
                print("⏰ Invalid timestamp, regenerating")
                return True
            
            # Check if product count changed significantly (>10%)
            try:
                products_data = self.product_service.get_all_products()
                current_count = len(products_data) if products_data else 0
                last_count = existing_data.get("product_count", 0)
                
                if last_count == 0 or abs(current_count - last_count) / last_count > 0.1:
                    print(f"📦 Product count changed significantly: {last_count} → {current_count}")
                    return True
            except:
                print("📦 Cannot check product count, regenerating")
                return True
            
            print("✅ Keywords are up-to-date, skipping regeneration")
            return False
            
        except Exception as e:
            print(f"❌ Error checking keyword status: {str(e)}")
            return True
    
    def generate_and_save_category_keywords(self, categories: List[str], force: bool = False) -> bool:
        """Generate category keywords and automatically save to file with smart caching"""
        try:
            # Check if regeneration is needed (unless forced)
            if not force and not self.should_regenerate_keywords(categories):
                return True
            
            print("🤖 Starting keyword generation...")
            
            # For large datasets, implement sampling strategy
            products_data = self.product_service.get_all_products()
            product_count = len(products_data) if products_data else 0
            
            if product_count > 1000:
                print(f"📊 Large dataset detected ({product_count} products), using sampling strategy")
                # Use sampling for large datasets to reduce API calls
                category_keywords = self.generate_category_keywords_with_sampling(categories, max_products_per_category=20)
            else:
                # Use full analysis for smaller datasets
                category_keywords = self.generate_category_keywords(categories)
            
            if category_keywords:
                # Save to file with metadata
                success = self.save_category_keywords_to_file(category_keywords, product_count=product_count)
                if success:
                    print(f"🎉 Successfully generated and saved keywords for {len(category_keywords)} categories")
                    return True
                else:
                    print("❌ Failed to save category keywords to file")
                    return False
            else:
                print("❌ No category keywords generated")
                return False
                
        except Exception as e:
            print(f"❌ Error in generate_and_save_category_keywords: {str(e)}")
            return False
    
    def generate_category_keywords_with_sampling(self, categories: List[str], max_products_per_category: int = 20) -> Dict[str, List[str]]:
        """Generate keywords using product sampling for large datasets"""
        if not self.openai_available:
            print("⚠️ OpenAI not available, cannot generate category keywords")
            return {}
        
        try:
            print(f"🎯 Generating keywords with sampling (max {max_products_per_category} products per category)")
            category_keywords = {}
            
            # Get all products to analyze
            products_data = self.product_service.get_all_products()
            if not products_data:
                print("⚠️ No products found")
                return {}
            
            # Group products by category
            products_by_category = {}
            for product_dict in products_data:
                category = product_dict.get('category', 'Unknown')
                if category not in products_by_category:
                    products_by_category[category] = []
                products_by_category[category].append(product_dict)
            
            for category in categories:
                try:
                    products_in_category = products_by_category.get(category, [])
                    
                    if not products_in_category:
                        print(f"⚠️ No products found for category '{category}', using basic keywords")
                        basic_keywords = self._generate_basic_category_keywords([category])
                        category_keywords[category] = basic_keywords.get(category, [])
                        continue
                    
                    # Sample products for analysis (mix of random and top products)
                    import random
                    sampled_products = []
                    
                    # Take top products (by rating/price) and random samples
                    sorted_products = sorted(products_in_category, 
                                           key=lambda x: (x.get('rating', 0), -x.get('price', 0)), 
                                           reverse=True)
                    
                    # Take top 60% and random 40%
                    top_count = min(int(max_products_per_category * 0.6), len(sorted_products))
                    random_count = min(max_products_per_category - top_count, len(sorted_products) - top_count)
                    
                    sampled_products.extend(sorted_products[:top_count])
                    if random_count > 0:
                        remaining = sorted_products[top_count:]
                        sampled_products.extend(random.sample(remaining, min(random_count, len(remaining))))
                    
                    print(f"📊 Analyzing {len(sampled_products)} sampled products for '{category}' (from {len(products_in_category)} total)")
                    
                    # Extract information from sampled products
                    brands = set()
                    product_names = []
                    descriptions = []
                    key_features = set()
                    
                    for product in sampled_products:
                        # Extract brand from product name
                        name = product.get('name', '')
                        if name:
                            product_names.append(name)
                            name_parts = name.split()
                            if name_parts:
                                potential_brand = name_parts[0]
                                if len(potential_brand) > 2 and potential_brand.isalpha():
                                    brands.add(potential_brand)
                        
                        # Extract description keywords
                        desc = product.get('description', '')
                        if desc:
                            descriptions.append(desc)
                            desc_lower = desc.lower()
                            tech_terms = ['wireless', 'bluetooth', 'smart', 'led', 'usb', 'hdmi', 'wifi', 'app', 'battery', 'rechargeable', 'portable', 'waterproof', 'noise', 'hd', '4k', 'gaming']
                            for term in tech_terms:
                                if term in desc_lower:
                                    key_features.add(term)
                    
                    # Create prompt with sampled data
                    brands_text = ', '.join(list(brands)[:8]) if brands else "various brands"
                    features_text = ', '.join(list(key_features)[:10]) if key_features else "standard features"
                    sample_names = '; '.join(product_names[:5]) if product_names else "no sample names"
                    
                    prompt = f"""Generate 20-25 search keywords for the "{category}" category based on sampled products from our inventory.
                    
                    SAMPLED PRODUCT DATA FROM OUR INVENTORY:
                    - Top brands we carry: {brands_text}
                    - Key features found: {features_text}
                    - Sample product names: {sample_names}
                    - Total products in category: {len(products_in_category)}
                    
                    Generate keywords that customers would use to search for these specific products. Include:
                    1. Category terms and synonyms
                    2. ACTUAL brand names from our inventory: {brands_text}
                    3. Technical features found in our products: {features_text}
                    4. Common search variations and use cases
                    5. Alternative names customers might use
                    
                    Focus on keywords that match the ACTUAL products we sell.
                    Return only comma-separated keywords, no explanations.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that generates search keywords based on sampled product inventory data. Focus on real brands and features found in the products."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=300
                    )
                    
                    result = response.choices[0].message.content.strip()
                    
                    # Parse keywords
                    keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
                    
                    # Remove duplicates
                    seen = set()
                    unique_keywords = []
                    for kw in keywords:
                        if kw.lower() not in seen:
                            seen.add(kw.lower())
                            unique_keywords.append(kw)
                    
                    category_keywords[category] = unique_keywords
                    print(f"✅ Generated {len(unique_keywords)} keywords for '{category}' (sampled {len(sampled_products)}/{len(products_in_category)} products)")
                    
                    # Shorter delay for sampling
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Error generating keywords for category '{category}': {str(e)}")
                    category_keywords[category] = []
            
            return category_keywords
            
        except Exception as e:
            print(f"❌ Error in generate_category_keywords_with_sampling: {str(e)}")
            return {}
    
    def save_category_keywords_to_file(self, category_keywords: Dict[str, List[str]], filename: str = "category_keywords.json", product_count: int = 0) -> bool:
        """Save category keywords to JSON file with metadata"""
        try:
            # Add metadata to the saved data
            keywords_data = {
                "generated_at": datetime.now().isoformat(),
                "total_categories": len(category_keywords),
                "product_count": product_count,
                "model_used": os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                "version": "2.0_product_aware",
                "categories": category_keywords
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(keywords_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Category keywords saved to {filename} (analyzed {product_count} products)")
            return True
        except Exception as e:
            print(f"❌ Error saving category keywords: {str(e)}")
            return False
    
    def _get_product_keywords(self, product: Product) -> List[str]:
        """Generate relevant keywords for better semantic matching"""
        # Try LLM-generated keywords first
        llm_keywords = self._get_llm_keywords(product)
        if llm_keywords:
            print(f"✅ LLM generated {len(llm_keywords)} keywords for {product.name}")
            
            # Also try to add category-specific keywords from our generated category keywords
            category_keywords = self._load_category_keywords()
            if category_keywords and product.category in category_keywords:
                category_kw = category_keywords[product.category]
                # Merge LLM keywords with category keywords, avoiding duplicates
                all_keywords = llm_keywords.copy()
                for kw in category_kw:
                    if kw.lower() not in [existing.lower() for existing in all_keywords]:
                        all_keywords.append(kw)
                print(f"✅ Enhanced with {len(category_kw)} category keywords, total: {len(all_keywords)}")
                return all_keywords
            
            return llm_keywords
        
        print(f"⚠️ LLM failed, using fallback keywords for {product.name}")
        
        # Fallback to hardcoded keywords if LLM fails
        keywords = []
        name_lower = product.name.lower()
        
        # Try to use category keywords from file first
        category_keywords = self._load_category_keywords()
        if category_keywords and product.category in category_keywords:
            keywords.extend(category_keywords[product.category])
            print(f"✅ Using {len(category_keywords[product.category])} saved category keywords for {product.category}")
        
        # Smartphone/Phone keywords (but not headphones/speakers)
        if any(word in name_lower for word in ['smartphone', '5g', 'mobile']) or \
           ('phone' in name_lower and not any(word in name_lower for word in ['headphone', 'earphone'])):
            keywords.extend(['phone','mobile phone','cell phone','smartphone','mobile device','cellular',
                             'iphone','android phone','handset','telephone','smart phone','5g phone',
                             'cellular phone','wireless phone','mobile smartphone'])
        if any(word in name_lower for word in ['laptop','computer','pc','macbook']):
            keywords.extend(['computer','laptop','notebook','pc','portable computer','macbook','mac','apple laptop'])
        if any(word in name_lower for word in ['gaming','game']):
            keywords.extend(['gaming','gamer','game','esports'])
        if 'mouse' in name_lower:
            keywords.extend(['mouse','computer mouse','gaming mouse','optical mouse'])
        if any(word in name_lower for word in ['headphone','headset','earphone']) and not any(word in name_lower for word in ['smartphone','5g']):
            keywords.extend(['headphones','headset','earphones','audio','music','wireless headphones'])
        if any(word in name_lower for word in ['tv','television','smart tv']):
            keywords.extend(['tv','television','smart tv','display','screen'])
        if any(word in name_lower for word in ['watch','smartwatch']):
            keywords.extend(['watch','smartwatch','wearable','fitness tracker'])
        if 'keyboard' in name_lower:
            keywords.extend(['keyboard', 'mechanical keyboard', 'gaming keyboard', 'typing'])
        
        # Speaker keywords
        if 'speaker' in name_lower or product.category.lower() == 'speaker':
            keywords.extend(['speaker', 'audio', 'sound', 'music', 'bluetooth speaker', 'wireless speaker', 'portable speaker', 'sound system', 'audio system'])
        
        # Lamp keywords
        if 'lamp' in name_lower or product.category.lower() == 'lamp':
            keywords.extend(['lamp', 'light', 'lighting', 'illumination', 'table lamp', 'desk lamp', 'floor lamp', 'ceiling lamp', 'bulb', 'brightness', 'led lamp', 'smart lamp', 'work lamp', 'reading lamp', 'ambient light'])
        
        # Tablet keywords
        if 'tablet' in name_lower:
            keywords.extend(['tablet','ipad','android tablet','portable device'])
        if product.category.lower() == 'furniture':
            if any(word in name_lower for word in ['chair','desk','table']):
                if 'chair' in name_lower:
                    keywords.extend(['chair','seat','office chair','gaming chair'])
                if any(word in name_lower for word in ['desk','table']):
                    keywords.extend(['desk','table','workstation','office desk'])
                if 'lamp' in name_lower:
                    keywords.extend(['lamp','light','lighting','desk lamp'])
        if product.category.lower() == 'appliances':
            if 'coffee' in name_lower:
                keywords.extend(['coffee','coffee maker','espresso','brewing'])
            if 'blender' in name_lower:
                keywords.extend(['blender','mixer','smoothie','kitchen appliance'])
        return keywords
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Load category keywords from JSON file"""
        try:
            with open("category_keywords.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Handle new format with metadata
                if "categories" in data:
                    print(f"📖 Loaded keywords for {data.get('total_categories', 0)} categories (generated: {data.get('generated_at', 'unknown')})")
                    return data["categories"]
                else:
                    # Handle old format (direct dictionary)
                    print(f"📖 Loaded keywords for {len(data)} categories (legacy format)")
                    return data
                    
        except FileNotFoundError:
            print("📄 Category keywords file not found")
            return {}
        except Exception as e:
            print(f"❌ Error loading category keywords: {str(e)}")
            return {}
    
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
            categories = self.product_service.get_categories()
            categories_str = ', '.join(categories)
            prompt = f"""
            Extract product search information from the following user input. 
            IMPORTANT: Only recognize these 5 categories: phone, camera, laptop, watch, camping gear. 
            If the input refers to any other category (clothes, jewelry, furniture, etc.), set category to null.
            
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search",
                "product_name": "specific product name if mentioned, otherwise null",
                "product_description": "specific product features, specifications, or descriptions mentioned, otherwise null",
                "filters": {{
                    "category": "category if mentioned ({categories_str}) or null",
                    "min_price": number or null,
                    "max_price": number or null,
                    "min_rating": number or null,
                    "min_discount": number or null
                }}
            }}
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

    def semantic_search(self, user_input: str, limit: int = 10, lang: str = "en") -> Dict[str, Any]:
        try:
            search_intent = self.extract_search_intent(user_input)
            product_name = search_intent.get("product_name", None)
            filters = search_intent.get("filters", {})
            product_category = filters.get("category", None)
            product_description = search_intent.get("product_description", None)
            # Use the full original query for better semantic search, enhanced with extracted info
            embedding_input = f"{product_category or ''} {product_name or ''} {product_description or ''}".strip()

            print(f"Search intent extracted: {search_intent}")
            print(f"Original query: {user_input}")
            print(f"Processed search_query: {embedding_input}")

            query_embedding = self.get_embedding(embedding_input)
            if not query_embedding:
                return {"status": "error", "message": "Failed to create query embedding"}

            where_clause = self._apply_metadata_filters(filters)

            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": limit,
                "include": ["metadatas", "documents", "distances"]
            }
            if where_clause:
                search_params["where"] = where_clause

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
                    print(f"DEBUG: Product {i} - ID: {metadata['id']}, Name: {metadata['name']}, Distance: {distance}, Similarity Score: {similarity_score}")
                    
                    # Lower threshold since we're now getting proper similarity scores
                    if similarity_score > 0.1:  # Much lower threshold for better results
                        product_data = {
                            "id": metadata["id"],  # Keep as string, don't convert to int
                            "name": metadata["name"],
                            "category": metadata["category"],
                            "price": metadata["price"],
                            "original_price": metadata["original_price"],
                            "rating": metadata["rating"],
                            "discount": metadata["discount"],
                            "imageUrl": metadata["imageUrl"],
                            "similarity_score": similarity_score
                        }
                        products.append(product_data)

            intro = self.make_intro_sentence(
                f"""User is searching for products: {user_input}. Found {len(products)} matching products. Encourage the decision warmly and funny.""",
                lang,
            )
            composed_response = self.compose_response(intro, products, lang)

            return {
                "status": "success",
                "search_intent": search_intent,
                "intro": composed_response["intro"],
                "header": composed_response["header"],
                "products": composed_response["products"],
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
    def make_intro_sentence(self, context: str, lang_code: str) -> str:
        instruction = (
            f"Write exactly 1 sentence in the language indicated by this ISO 639-1 code: {lang_code}. "
            "Use a warm and cheerful tone. No bullet points. Max ~30 words."
        )
        prompt = f"{instruction}\nContext: {context}"
        text = self.llm.invoke(prompt).content.strip()
        if "." in text and lang_code == "en":
            text = text.split(".")[0].strip() + "."
        return text

    def compose_response(self, intro: str, items, lang_code: str):
        header = self.HEADER_BY_LANG.get(lang_code, self.HEADER_BY_LANG["en"])
        return {"intro": intro, "header": header, "products": items}

    def truncate_conversation_history(self, messages: List[Dict[str, str]], max_messages: int = 8) -> List[Dict[str, str]]:
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
        
        # Keep last N conversation messages
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
        # Truncate conversation history to prevent token overflow
        messages = self.truncate_conversation_history(messages, max_messages=8)
        
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
            "total_results": ai_response_data.get("total_results", 0),
            "messages": messages,
        }
