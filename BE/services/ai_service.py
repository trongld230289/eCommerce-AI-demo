import os
import json
import asyncio
import sys
import tempfile
import io
from typing import List, Dict, Any, Optional
import numpy as np
from dotenv import load_dotenv

# Handle OpenAI import with proper error handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenAI not available: {e}")
    OPENAI_AVAILABLE = False
    openai = None

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

class AIService:
    def __init__(self):
        # Check if required dependencies are available
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required but not available. Please install with: pip install chromadb")
        
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"OpenAI API Key: {api_key[:10] if api_key else 'None'}...")
        
        # Initialize OpenAI client only if API key and library are available
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
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            raise
        
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
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []
    
    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        """Transcribe audio to text using OpenAI Whisper API"""
        if not self.openai_available:
            return {"status": "error", "message": "OpenAI API key not available. Cannot transcribe audio."}
            
        try:
            # Debug: Print file info
            print(f"Transcribing audio file: {audio_file}")
            print(f"File type: {type(audio_file)}")
            
            # Try to get file info if available
            if hasattr(audio_file, 'filename'):
                print(f"File name: {audio_file.filename}")
            if hasattr(audio_file, 'content_type'):
                print(f"Content type: {audio_file.content_type}")
            
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
                    
                    if embedding:
                        embeddings.append(embedding)
                        documents.append(text)
                        metadatas.append(self._prepare_product_metadata(product))
                        ids.append(f"product_{product.id}")
                
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
                    "min_price": number or null,
                    "max_price": number or null,
                    "min_rating": number or null,
                    "min_discount": number or null
                }}
            }}
            
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
        if (min_p := filters.get("min_price")) is not None:
            clauses.append({"price": {"$gte": float(min_p)}})
        if (max_p := filters.get("max_price")) is not None:
            clauses.append({"price": {"$lte": float(max_p)}})

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
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    
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
            
            if transcription_result["status"] != "success":
                return transcription_result
            
            transcribed_text = transcription_result["text"]
            
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
