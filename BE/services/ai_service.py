import os
import json
import asyncio
import sys
import tempfile
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
import chromadb
from chromadb.config import Settings
import numpy as np
from dotenv import load_dotenv

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
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"OpenAI API Keyaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: {api_key}")
        
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
        if 'speaker' in name_lower or product.category.lower() == 'speaker':
            keywords.extend(['speaker', 'audio', 'sound', 'music', 'bluetooth speaker', 'wireless speaker', 'portable speaker', 'sound system', 'audio system'])
        
        # Lamp keywords
        if 'lamp' in name_lower or product.category.lower() == 'lamp':
            keywords.extend(['lamp', 'light', 'lighting', 'illumination', 'table lamp', 'desk lamp', 'floor lamp', 'ceiling lamp', 'bulb', 'brightness', 'led lamp', 'smart lamp', 'work lamp', 'reading lamp', 'ambient light'])
        
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
            categories = self.product_service.get_categories()
            categories_str = ', '.join(categories)
            prompt = f"""
            Extract product search information from the following user input. 
            Return a JSON object with the following structure:
            {{
                "search_query": "main search terms for semantic search",
                "filters": {{
                    "category": "category if mentioned ({categories_str}) or null",
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
