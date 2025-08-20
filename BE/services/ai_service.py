import os
import json
import asyncio
<<<<<<< HEAD
=======
import string
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
import sys
import tempfile
import io
from typing import List, Dict, Any, Optional
<<<<<<< HEAD
import openai
import chromadb
from chromadb.config import Settings
import numpy as np
from dotenv import load_dotenv
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

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
<<<<<<< HEAD
=======
from services.middleware_service import MiddlewareService
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

# Load environment variables
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path)

<<<<<<< HEAD
class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client only if API key is available
        if api_key and api_key != "None":
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.openai_available = True
        else:
            print("Warning: OpenAI API key not found. AI features will be limited.")
            self.openai_client = None
            self.openai_available = False
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection name for products
        self.collection_name = "products_embeddings"
        self.embedding_model = "text-embedding-3-small"
        
        # Initialize or get collection
        self._initialize_collection()
        
        # Initialize ProductService
        self.product_service = ProductService()
    
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection"""
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.collection_name
            )
        except Exception:
            # Create collection if it doesn't exist
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using OpenAI API"""
        if not self.openai_available:
            print("OpenAI not available, returning empty embedding")
            return []
            
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
=======
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
        self.middleware_service = MiddlewareService()

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
            result = self.semantic_search(query, 10, self.USER_LANG_CODE, searchFromTool="find_products")
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

            # Get external gift products with labels
            external_products = self._get_external_gift_products()

            composed_response = self.make_response_sentence(user_input, external_products, self.USER_LANG_CODE)
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []
<<<<<<< HEAD
    
    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        """Transcribe audio to text using OpenAI Whisper API"""
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot transcribe audio."}
            
        try:
            # Debug: Print file info
            print(f"Transcribing audio file: {audio_file}")
            print(f"File type: {type(audio_file)}")
            
            # Try to get file info if available
=======

    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot transcribe audio."}
        try:
            print(f"Transcribing audio file: {audio_file}")
            print(f"File type: {type(audio_file)}")
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            if hasattr(audio_file, 'filename'):
                print(f"File name: {audio_file.filename}")
            if hasattr(audio_file, 'content_type'):
                print(f"Content type: {audio_file.content_type}")
<<<<<<< HEAD
            
            # Try to convert audio to a compatible format if needed
            processed_file = self._process_audio_file(audio_file)
                
            # Use Whisper to transcribe the audio
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=processed_file,
                response_format="text"
            )
            
            # Clean up temporary file if created
            if processed_file != audio_file and hasattr(processed_file, 'close'):
                processed_file.close()
            
            return {
                "status": "success",
                "text": response,
                "message": "Audio transcribed successfully"
            }
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return {
                "status": "error", 
                "message": f"Transcription failed: {str(e)}"
            }
    
    def _process_audio_file(self, audio_file):
        """Process audio file to ensure compatibility with Whisper API"""
        try:
            # Read the file content
            audio_file.seek(0)  # Reset file pointer
            file_content = audio_file.read()
            
            print(f"Original file size: {len(file_content)} bytes")
            
            # Get content type from the upload file
            content_type = getattr(audio_file, 'content_type', '')
            filename = getattr(audio_file, 'filename', 'audio')
            
            print(f"Content type: {content_type}")
            print(f"Filename: {filename}")
            
            # Create a proper file-like object with name attribute
            audio_buffer = io.BytesIO(file_content)
            
            # Determine file extension and set proper name
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
                # Default to webm if unknown
                audio_buffer.name = 'audio.webm'
            
            print(f"Processed file name: {audio_buffer.name}")
            
            return audio_buffer
                
        except Exception as e:
            print(f"Error processing audio file: {str(e)}")
            audio_file.seek(0)  # Reset for Whisper
            return audio_file
    
    def _prepare_product_text(self, product: Product) -> str:
        """Prepare product text for embedding"""
        # Get relevant keywords first for better semantic matching
        keywords = self._get_product_keywords(product)
        
        text_parts = []
        
        # Add keywords first for higher importance
        if keywords:
            # Add primary keywords multiple times for higher weight
            primary_keywords = keywords[:3]  # First 3 keywords
            text_parts.extend(primary_keywords)
            text_parts.extend(keywords)
        
        # Then add product name and details
        text_parts.extend([
            product.name,
            product.category,
        ])
        
        if product.description:
            text_parts.append(product.description)
        
        return " ".join(text_parts)
    
    def _get_product_keywords(self, product: Product) -> List[str]:
        """Generate relevant keywords for better semantic matching"""
        keywords = []
        name_lower = product.name.lower()
        
        # Smartphone/Phone keywords (but not headphones/speakers)
        if any(word in name_lower for word in ['smartphone', '5g', 'mobile']) or \
           ('phone' in name_lower and not any(word in name_lower for word in ['headphone', 'earphone'])):
            keywords.extend([
                'phone', 'mobile phone', 'cell phone', 'smartphone', 'mobile device', 'cellular',
                'iphone', 'android phone', 'mobile phone', 'handset', 'telephone', 'smart phone',
                '5g phone', 'cellular phone', 'wireless phone', 'mobile smartphone'
            ])
        
        # Computer/Laptop keywords  
        if any(word in name_lower for word in ['laptop', 'computer', 'pc', 'macbook']):
            keywords.extend(['computer', 'laptop', 'notebook', 'pc', 'portable computer', 'macbook', 'mac', 'apple laptop'])
        
        # Gaming keywords
        if any(word in name_lower for word in ['gaming', 'game']):
            keywords.extend(['gaming', 'gamer', 'game', 'esports'])
        
        # Mouse keywords
        if 'mouse' in name_lower:
            keywords.extend(['mouse', 'computer mouse', 'gaming mouse', 'optical mouse'])
        
        # Headphone keywords (separate from phone)
        if any(word in name_lower for word in ['headphone', 'headset', 'earphone']) and \
           not any(word in name_lower for word in ['smartphone', '5g']):
            keywords.extend(['headphones', 'headset', 'earphones', 'audio', 'music', 'wireless headphones'])
        
        # TV keywords
        if any(word in name_lower for word in ['tv', 'television', 'smart tv']):
            keywords.extend(['tv', 'television', 'smart tv', 'display', 'screen'])
        
        # Watch keywords
        if any(word in name_lower for word in ['watch', 'smartwatch']):
            keywords.extend(['watch', 'smartwatch', 'wearable', 'fitness tracker'])
        
        # Keyboard keywords
        if 'keyboard' in name_lower:
            keywords.extend(['keyboard', 'mechanical keyboard', 'gaming keyboard', 'typing'])
        
        # Speaker keywords
        if 'speaker' in name_lower:
            keywords.extend(['speaker', 'audio', 'sound', 'music', 'bluetooth speaker'])
        
        # Tablet keywords
        if 'tablet' in name_lower:
            keywords.extend(['tablet', 'ipad', 'android tablet', 'portable device'])
        
        # Furniture keywords
        if product.category.lower() == 'furniture':
            if any(word in name_lower for word in ['chair', 'desk', 'table']):
                if 'chair' in name_lower:
                    keywords.extend(['chair', 'seat', 'office chair', 'gaming chair'])
                if any(word in name_lower for word in ['desk', 'table']):
                    keywords.extend(['desk', 'table', 'workstation', 'office desk'])
                if 'lamp' in name_lower:
                    keywords.extend(['lamp', 'light', 'lighting', 'desk lamp'])
        
        # Appliance keywords
        if product.category.lower() == 'appliances':
            if 'coffee' in name_lower:
                keywords.extend(['coffee', 'coffee maker', 'espresso', 'brewing'])
            if 'blender' in name_lower:
                keywords.extend(['blender', 'mixer', 'smoothie', 'kitchen appliance'])
        
        return keywords
    
    def _prepare_product_metadata(self, product: Product) -> Dict[str, Any]:
        """Prepare product metadata for ChromaDB"""
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
    
    async def embed_all_products(self) -> Dict[str, Any]:
        """Get all products, create embeddings, and store in ChromaDB"""
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot create embeddings."}
            
        try:
            # Get all products from Firebase
            products_data = self.product_service.get_all_products()
            
            if not products_data:
                return {"status": "error", "message": "No products found"}
            
            # Convert dict data to Product objects
=======

    # ---------- Index / Search ----------
    async def embed_all_products(self) -> Dict[str, Any]:
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot create embeddings."}
        try:
            products_data = self.product_service.get_all_products()
            if not products_data:
                return {"status": "error", "message": "No products found"}
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            products = []
            for product_dict in products_data:
                try:
                    product = Product(**product_dict)
                    products.append(product)
                except Exception as e:
                    print(f"Error converting product {product_dict.get('id', 'unknown')}: {e}")
                    continue
<<<<<<< HEAD
            
            if not products:
                return {"status": "error", "message": "No valid products found"}
            
            # Clear existing collection
            self.chroma_client.delete_collection(self.collection_name)
            self._initialize_collection()
            
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            print(f"Processing {len(products)} products...")
            
            # Process products in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                
                for product in batch:
                    # Prepare text for embedding
                    text = self._prepare_product_text(product)
                    
                    # Get embedding
                    embedding = self.get_embedding(text)
                    
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                    if embedding:
                        embeddings.append(embedding)
                        documents.append(text)
                        metadatas.append(self._prepare_product_metadata(product))
                        ids.append(f"product_{product.id}")
<<<<<<< HEAD
                
                # Small delay between batches to respect rate limits
                if i + batch_size < len(products):
                    await asyncio.sleep(1)
            
            # Add to ChromaDB
            if embeddings:
                self.collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                return {
                    "status": "success",
                    "message": f"Successfully embedded {len(embeddings)} products",
                    "total_products": len(embeddings)
                }
            else:
                return {"status": "error", "message": "Failed to create embeddings"}
                
        except Exception as e:
            print(f"Error embedding products: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def extract_search_intent(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to extract product search intent from user input"""
        if not self.openai_available:
            print("OpenAI not available, returning simple intent")
            return {
                "search_query": user_input,
                "filters": {}
            }
            
        try:
            prompt = f"""
            Extract product search information from the following user input. 
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search",
                "filters": {{
                    "category": "category if mentioned (Camera, Laptop, Phone, Watch) or null",
=======
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
            
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search",
                "product_name": "specific product name if mentioned, otherwise null",
                "product_description": "specific product features, specifications, or descriptions mentioned, otherwise null",
                "filters": {{
                    "category": "ONLY one of: phone, camera, laptop, watch, camping gear - or null if not these categories",
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                    "min_price": number or null,
                    "max_price": number or null,
                    "min_rating": number or null,
                    "min_discount": number or null
                }}
            }}
<<<<<<< HEAD
            
            User input: "{user_input}"
            
            Examples:
            - "I want a cheap laptop" -> {{"search_query": "laptop computer", "filters": {{"category": "Laptop", "max_price": 1000}}}}
            - "Show me phones under $500" -> {{"search_query": "phones", "filters": {{"category": "Phone", "max_price": 500}}}}
            - "I need a good quality watch" -> {{"search_query": "watch", "filters": {{"category": "Watch", "min_rating": 4}}}}
            - "camera" -> {{"search_query": "camera", "filters": {{"category": "Camera"}}}}
            - "Give me some camera" -> {{"search_query": "camera", "filters": {{"category": "Camera"}}}}
            - "I want finding some cameras with new model" -> {{"search_query": "cameras", "filters": {{"category": "Camera", "min_rating": 4}}}}

            Return only the JSON object, no additional text.
            """
            
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL_ID"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts product search intent from user queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                search_intent = json.loads(result)
                return search_intent
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "search_query": user_input,
                    "filters": {}
                }
                
        except Exception as e:
            print(f"Error extracting search intent: {str(e)}")
            return {
                "search_query": user_input,
                "filters": {}
            }
    
    def _apply_metadata_filters(self, filters: Dict[str, Any]) -> Dict[str, Any] | None:
        """Build a ChromaDB-compatible where clause.
        - If 0 clauses  -> None
        - If 1 clause    -> return that clause (no $and)
        - If >=2 clauses -> wrap with {"$and": [...]}
        """
        clauses: list[dict] = []

        # Category (string equality)
        if (cat := filters.get("category")) is not None:
            clauses.append({"category": {"$eq": str(cat)}})

        # Price (numeric)
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        if (min_p := filters.get("min_price")) is not None:
            clauses.append({"price": {"$gte": float(min_p)}})
        if (max_p := filters.get("max_price")) is not None:
            clauses.append({"price": {"$lte": float(max_p)}})
<<<<<<< HEAD

        # Rating (numeric)
        if (min_r := filters.get("min_rating")) is not None:
            clauses.append({"rating": {"$gte": float(min_r)}})

        # Discount (numeric)
        if (min_d := filters.get("min_discount")) is not None:
            clauses.append({"discount": {"$gte": float(min_d)}})

        # Add more fields if needed, e.g. brand/panel:
        if (brand := filters.get("brand")) is not None:
            clauses.append({"brand": {"$eq": str(brand)}})
        if (panel := filters.get("panel")) is not None:
            clauses.append({"panel": {"$eq": str(panel)}})

        # Return according to number of clauses
=======
        if (min_r := filters.get("min_rating")) is not None:
            clauses.append({"rating": {"$gte": float(min_r)}})
        if (min_d := filters.get("min_discount")) is not None:
            clauses.append({"discount": {"$gte": float(min_d)}})
        if (brand := filters.get("brand")) is not None:
            clauses.append({"brand": {"$eq": str(brand)}})
       
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

<<<<<<< HEAD
    
    async def semantic_search(self, user_input: str, limit: int = 10) -> Dict[str, Any]:
        """Perform semantic search on products"""
        try:
            # Extract search intent using LLM
            search_intent = self.extract_search_intent(user_input)
            search_query = search_intent.get("search_query", user_input)
            filters = search_intent.get("filters", {})
            
            # Get embedding for search query
            query_embedding = self.get_embedding(search_query)
            
            if not query_embedding:
                return {"status": "error", "message": "Failed to create query embedding"}
            
            # Prepare metadata filters
            where_clause = self._apply_metadata_filters(filters)
            
            # Search in ChromaDB
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": limit,
                "include": ["metadatas", "documents", "distances"]
            }
            
            if where_clause:
                search_params["where"] = where_clause
            
            results = self.collection.query(**search_params)
            
            # Process results
            products = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    similarity_score = 1 - results["distances"][0][i]  # Convert distance to similarity
                    
                    # Filter out products with low similarity scores
                    if similarity_score > 0.35:
                        product_data = {
                            "id": int(metadata["id"]),
=======
    def semantic_search(self, user_input: str, limit: int = 10, lang: str = "en", searchFromTool:str = "find_products") -> Dict[str, Any]:
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
                    if similarity_score > 0.1:  # Much lower threshold for better results
                        product_data = {
                            "id": metadata["id"],  # Keep as string, don't convert to int
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                            "name": metadata["name"],
                            "category": metadata["category"],
                            "price": metadata["price"],
                            "original_price": metadata["original_price"],
                            "rating": metadata["rating"],
                            "discount": metadata["discount"],
                            "imageUrl": metadata["imageUrl"],
<<<<<<< HEAD
                            "similarity_score": similarity_score
                        }
                        products.append(product_data)
            
            return {
                "status": "success",
                "search_intent": search_intent,
                "products": products,
                "total_results": len(products)
            }
            
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return {"status": "error", "message": f"Search error: {str(e)}"}
    
    async def voice_search(self, audio_file, limit: int = 10) -> Dict[str, Any]:
        """Perform voice search: transcribe audio and then search products"""
        try:
            # Step 1: Transcribe audio to text
            transcription_result = self.transcribe_audio(audio_file)
            
=======
                            "similarity_score": similarity_score,
                            "showLabel": "product" if searchFromTool == "find_products" else ("gift" if searchFromTool == "find_gifts" else None)
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
                
            # Limit results to requested amount
            products = filtered_products[:limit]
            
            print(f"DEBUG: Semantic search found {len(results['metadatas'][0] if results['metadatas'] else [])} total")
            print(f"DEBUG: After similarity filter: {len(products)} products") 
            print(f"DEBUG: After price/rating filters: {len(filtered_products)} products")
            print(f"DEBUG: Final result (limited to {limit}): {len(products)} products")

            composed_response = self.make_response_sentence(user_input, products, lang)
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
            if transcription_result["status"] != "success":
                return transcription_result
            
            transcribed_text = transcription_result["text"]
            
<<<<<<< HEAD
            # Step 2: Perform semantic search with transcribed text
            search_result = await self.semantic_search(transcribed_text, limit)
            
            # Add transcription info to the result
            if search_result["status"] == "success":
                search_result["transcribed_text"] = transcribed_text
                search_result["original_query_type"] = "voice"
            
            return search_result
            
        except Exception as e:
            print(f"Error in voice search: {str(e)}")
            return {"status": "error", "message": f"Voice search error: {str(e)}"}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection"""
        try:
            count = self.collection.count()
            return {
                "status": "success",
                "collection_name": self.collection_name,
                "total_products": count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            return {"status": "error", "message": f"Error getting stats: {str(e)}"}
=======
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

    def make_response_sentence(self, user_input: str, products: List[Dict], lang_code: str) -> Dict[str, str]:
        try:
            product_count = len(products)
            
            # Single comprehensive prompt for all three fields
            prompt = f"""
            You are a multilingual e-commerce assistant. Generate a JSON response with exactly these 3 fields for a product search result.

            USER SEARCH: "{user_input}"
            PRODUCTS FOUND: {product_count}
            LANGUAGE CODE: {lang_code}

            Generate response in the language indicated by the language code ({lang_code}).

            Return ONLY a valid JSON object with these exact keys:
            {{
                "intro": "A warm, encouraging 1-sentence introduction about the search results (max 30 words). Be cheerful and engaging.",
                "header": "A short subtitle introducing the product list below (max 15 words). Like 'Here are your product suggestions:' but more natural.",
                "show_all_product": "A message asking if user wants to see all {product_count} results on products page (max 25 words). ONLY include this if product_count > 3, otherwise return empty string."
            }}

            Context guidelines:
            - If {product_count} == 0: Make intro encouraging and helpful
            - If {product_count} > 0: Make intro excited about the findings  
            - If {product_count} > 3: Include show_all_product message, otherwise empty string ""
            - Use natural, conversational tone appropriate for the language
            - Be consistent with the language code throughout

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
                print(f"Failed to parse LLM JSON response: {e}")
                print(f"Raw response: {response}")
                raise Exception("LLM returned invalid JSON")
            
        except Exception as e:
            print(f"Error in make_response_sentence: {str(e)}")
            # Fallback to static messages
            fallback_intros = {
                "en": f"I found {len(products)} products for your search!" if products else "Sorry, no products found for your search.",
                "vi": f"Tôi tìm thấy {len(products)} sản phẩm cho bạn!" if products else "Xin lỗi, không tìm thấy sản phẩm nào.",
                "ko": f"검색에서 {len(products)}개 제품을 찾았습니다!" if products else "죄송합니다. 제품을 찾을 수 없습니다.",
                "ja": f"検索で{len(products)}個の商品を見つけました！" if products else "申し訳ございませんが、商品が見つかりませんでした。"
            }
            
            fallback_headers = {
                "en": "Here are your product suggestions:",
                "vi": "Đây là những sản phẩm gợi ý cho bạn:",
                "ko": "제품 추천 목록입니다:",
                "ja": "おすすめ商品一覧："
            }
            
            fallback_show_all = {
                "en": f"I found {len(products)} total results. Would you like to see all of them?" if len(products) > 3 else "",
                "vi": f"Tôi tìm thấy {len(products)} kết quả. Bạn có muốn xem tất cả không?" if len(products) > 3 else "",
                "ko": f"{len(products)}개의 결과를 찾았습니다. 모두 보시겠습니까?" if len(products) > 3 else "",
                "ja": f"{len(products)}個の結果が見つかりました。すべて見ますか？" if len(products) > 3 else ""
            }
            
            return {
                "intro": fallback_intros.get(lang_code, fallback_intros["en"]),
                "header": fallback_headers.get(lang_code, fallback_headers["en"]),
                "show_all_product": fallback_show_all.get(lang_code, fallback_show_all["en"])
            }

    def compose_response(self, intro: str, items, lang_code: str):
        header = self.HEADER_BY_LANG.get(lang_code, self.HEADER_BY_LANG["en"])
        return {"intro": intro, "header": header, "products": items}

    def _get_external_gift_products(self) -> List[Dict[str, Any]]:
        """
        Get products from external gift recommendations with labels assigned to showLabel.
        
        Returns:
            List of product dictionaries with showLabel field
        """
        try:
            # Get external gift recommendations
            gift_recommendations = self.middleware_service.find_gifts_external()
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
                            "showLabel": label  # Assign the label from external recommendations
                        }
                        external_products.append(external_product)
            
            print(f"DEBUG _get_external_gift_products - external products with labels: {external_products}")
            return external_products
            
        except Exception as e:
            print(f"Error getting external gift products: {str(e)}")
            return []


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
            "show_all_product": ai_response_data.get("show_all_product"),  # Add missing show_all_product field
            "total_results": ai_response_data.get("total_results", 0),
            "messages": messages,
        }
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
