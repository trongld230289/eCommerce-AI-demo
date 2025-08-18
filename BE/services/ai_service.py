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
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv

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
You are a shopping assistant that MUST use tools to find products.

IMPORTANT RULES:
1. ALWAYS call either `find_products` or `find_gifts` tool for ANY product search request
2. NEVER give direct answers without using tools first
3. If user mentions recipients (mom, dad, friend, etc.) or gift occasions, call `find_gifts`
4. Otherwise, call `find_products` 
5. Pass the user's query directly to the tool - don't ask for clarification

CATEGORY RESTRICTIONS:
- You can ONLY recommend products in these 4 categories: phone, camera, laptop, watch
- If user asks for anything outside these categories (clothes, jewelry, furniture, etc.), politely explain that you only help with: phone, camera, laptop, and watch products
- Always try to suggest alternatives within the allowed categories if possible

Examples:
- User: "phone" → Call find_products("phone")  
- User: "laptop for work" → Call find_products("laptop for work")
- User: "gift for mom" → Call find_gifts("gift for mom")
- User: "birthday present" → Call find_gifts("birthday present")
- User: "clothes" → Explain limitations and suggest alternatives like "smartwatch for fitness tracking"

You must call a tool on EVERY valid product search request. Do not provide generic responses.
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
            max_tokens=600,
        )

        # ---- Define tools as closures (no exposed self param)
        class FindProductsInput(BaseModel):
            query: str = Field(..., description="Free-text product search.")

        @tool("find_products", args_schema=FindProductsInput, return_direct=True)
        def find_products(query: str) -> str:
            """Find and recommend products based on user's shopping needs. Only searches in: phone, camera, laptop, watch categories."""
            
            # Return JSON-encoded string for consistent downstream parsing
            result = self.semantic_search(query, 10, self.USER_LANG_CODE)
            return json.dumps(result, ensure_ascii=False)

        class FindGiftsInput(BaseModel):
            recipient: str = Field(..., description="e.g., 'my mom'")
            user_input: str = Field(..., description="User's input query for context")
            category: Optional[str] = Field(default=None, description="Gift interest/category, e.g., 'phone'")
            occasion: Optional[str] = Field(default=None, description="e.g., 'birthday'")

        @tool("find_gifts", args_schema=FindGiftsInput, return_direct=True)
        def find_gifts(recipient: str,  user_input: str,category: Optional[str], occasion: Optional[str] = "general") -> str:
            """
            Recommend gifts for a recipient. Category must be one of: phone/camera/laptop/watch.
            If category is not provided or invalid, return a clarification message.
            """
            print(f"DEBUG find_gifts - recipient: {recipient}, user_input: {user_input}, category: {category}")
            
            # If category is provided, use it for search; otherwise use original user_input
            search_query = category if category else user_input
            print(f"DEBUG find_gifts - search_query: {search_query}")
            
            result = self.semantic_search(search_query, 5, self.USER_LANG_CODE)
            result["recipient"] = recipient
            result["requested_category"] = category
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
        keywords = self._get_product_keywords(product)
        text_parts = []
        if keywords:
            primary_keywords = keywords[:3]
            text_parts.extend(primary_keywords)
            text_parts.extend(keywords)
        text_parts.extend([product.name, product.category])
        if product.description:
            text_parts.append(product.description)
        return " ".join(text_parts)

    def _get_product_keywords(self, product: Product) -> List[str]:
        keywords = []
        name_lower = product.name.lower()
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
            keywords.extend(['keyboard','mechanical keyboard','gaming keyboard','typing'])
        if 'speaker' in name_lower:
            keywords.extend(['speaker','audio','sound','music','bluetooth speaker'])
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
            IMPORTANT: Only recognize these 4 categories: phone, camera, laptop, watch. 
            If the input refers to any other category (clothes, jewelry, furniture, etc.), set category to null.
            
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search",
                "product_name": "specific product name if mentioned, otherwise null",
                "product_description": "specific product features, specifications, or descriptions mentioned, otherwise null",
                "filters": {{
                    "category": "ONLY one of: phone, camera, laptop, watch - or null if not these categories",
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
                    {"role": "system", "content": "You are a helpful assistant that extracts product search intent from user queries. ONLY recognize these 4 product categories: phone, camera, laptop, watch. Ignore any other categories."},
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
            embedding_input = f"{product_category} {product_name or ''} {product_description or ''}".strip()

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
            valid_categories = ["phone", "camera", "laptop", "watch"]
            
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    # Only include products from valid categories
                    if metadata["category"].lower() not in valid_categories:
                        continue
                        
                    similarity_score = 1 - results["distances"][0][i]
                    if similarity_score > 0.35:
                        product_data = {
                            "id": int(metadata["id"]),
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
                f"User is searching for products: {user_input}. Found {len(products)} matching products. Encourage the decision warmly.",
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

    # ---------- Chat middleware ----------
    async def semantic_search_middleware(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # last user input
        user_input = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        # update language ON INSTANCE
        self.USER_LANG_CODE = self.detect_language(user_input)

        # ensure system message (optional since we also pass state_modifier)
        agent_messages = messages.copy()
        # if not agent_messages or agent_messages[0].get("role") != "system":
        #     agent_messages.insert(0, {"role": "system", "content": SYSTEM_INSTRUCTIONS})

        print(f"DEBUG: User input: {user_input}")
        print(f"DEBUG: Language detected: {self.USER_LANG_CODE}")
        print(f"DEBUG: Messages before agent: {agent_messages}")

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
