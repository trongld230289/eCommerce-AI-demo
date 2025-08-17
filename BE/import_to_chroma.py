#!/usr/bin/env python3
"""
ChromaDB Product Import Script
Test script to import products into ChromaDB with robust error handling
"""

import os
import sys
import asyncio
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
import chromadb
from chromadb.config import Settings

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from models import Product
from product_service import ProductService

# Load environment variables
load_dotenv()

class ChromaDBImporter:
    def __init__(self):
        """Initialize the ChromaDB importer"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 API Key: {self.api_key[:20]}..." if self.api_key else "❌ No API Key found")
        
        # Initialize OpenAI client
        if self.api_key:
            self.openai_client = openai.OpenAI(api_key=self.api_key)
            self.openai_available = True
            print("✅ OpenAI client initialized")
        else:
            print("❌ OpenAI API key not found")
            return
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ ChromaDB client initialized")
        except Exception as e:
            print(f"❌ ChromaDB initialization error: {e}")
            return
        
        # Collection settings
        self.collection_name = "products_embeddings"
        self.embedding_model = "text-embedding-3-small"
        
        # Initialize ProductService
        try:
            self.product_service = ProductService()
            print("✅ ProductService initialized")
        except Exception as e:
            print(f"❌ ProductService initialization error: {e}")
            return
    
    def _initialize_collection(self):
        """Initialize or recreate the ChromaDB collection"""
        try:
            # Try to delete existing collection
            try:
                self.chroma_client.delete_collection(self.collection_name)
                print("🗑️ Deleted existing collection")
            except Exception:
                print("ℹ️ No existing collection to delete")
            
            # Create new collection
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Created new ChromaDB collection")
            
        except Exception as e:
            print(f"❌ Collection initialization error: {e}")
            raise e
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text with error handling"""
        try:
            print(f"🔄 Getting embedding for: {text[:50]}...")
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            print(f"✅ Got embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            print(f"❌ Embedding error: {str(e)}")
            return []
    
    def prepare_product_text(self, product: Product) -> str:
        """Prepare product text for embedding"""
        text_parts = [
            f"Product: {product.name}",
            f"Category: {product.category}",
            f"Price: ${product.price}"
        ]
        
        if hasattr(product, 'description') and product.description:
            text_parts.append(f"Description: {product.description}")
        
        if hasattr(product, 'rating') and product.rating:
            text_parts.append(f"Rating: {product.rating}/5")
        
        return " | ".join(text_parts)
    
    def prepare_product_metadata(self, product: Product) -> Dict[str, Any]:
        """Prepare product metadata for ChromaDB"""
        metadata = {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "price": float(product.price)
        }
        
        # Add optional fields if they exist
        if hasattr(product, 'original_price') and product.original_price:
            metadata["original_price"] = float(product.original_price)
        
        if hasattr(product, 'rating') and product.rating:
            metadata["rating"] = float(product.rating)
        
        if hasattr(product, 'discount') and product.discount:
            metadata["discount"] = float(product.discount)
        
        if hasattr(product, 'imageUrl') and product.imageUrl:
            metadata["imageUrl"] = product.imageUrl
        
        return metadata
    
    async def import_products_to_chroma(self) -> Dict[str, Any]:
        """Import all products to ChromaDB with robust error handling"""
        try:
            print("🚀 Starting ChromaDB import process...")
            
            # Initialize collection
            self._initialize_collection()
            
            # Get products from Firebase
            print("📥 Fetching products from Firebase...")
            products_data = self.product_service.get_all_products()
            
            if not products_data:
                return {"status": "error", "message": "No products found in Firebase"}
            
            print(f"📊 Found {len(products_data)} products in Firebase")
            
            # Convert to Product objects
            products = []
            for i, product_dict in enumerate(products_data, 1):
                try:
                    product = Product(**product_dict)
                    products.append(product)
                    print(f"✅ Product {i}: {product.name}")
                except Exception as e:
                    print(f"❌ Error with product {i}: {e}")
                    continue
            
            if not products:
                return {"status": "error", "message": "No valid products found"}
            
            print(f"✅ Successfully converted {len(products)} products")
            
            # Process products one by one for better error handling
            successful_embeddings = 0
            failed_embeddings = 0
            
            for i, product in enumerate(products, 1):
                try:
                    print(f"\\n📦 Processing product {i}/{len(products)}: {product.name}")
                    
                    # Prepare text for embedding
                    text = self.prepare_product_text(product)
                    print(f"📝 Text prepared: {len(text)} characters")
                    
                    # Get embedding
                    embedding = self.get_embedding(text)
                    
                    if not embedding:
                        print(f"❌ Failed to get embedding for {product.name}")
                        failed_embeddings += 1
                        continue
                    
                    # Prepare metadata
                    metadata = self.prepare_product_metadata(product)
                    
                    # Add to ChromaDB
                    self.collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        metadatas=[metadata],
                        ids=[f"product_{product.id}"]
                    )
                    
                    successful_embeddings += 1
                    print(f"✅ Successfully added {product.name} to ChromaDB")
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Error processing {product.name}: {str(e)}")
                    failed_embeddings += 1
                    continue
            
            # Final results
            result = {
                "status": "success" if successful_embeddings > 0 else "error",
                "message": f"Import completed: {successful_embeddings} successful, {failed_embeddings} failed",
                "successful": successful_embeddings,
                "failed": failed_embeddings,
                "total": len(products)
            }
            
            print(f"\\n🎉 Import Results:")
            print(f"   ✅ Successful: {successful_embeddings}")
            print(f"   ❌ Failed: {failed_embeddings}")
            print(f"   📊 Total: {len(products)}")
            
            # Verify collection
            try:
                collection_count = self.collection.count()
                print(f"\\n🔍 ChromaDB Collection Verification:")
                print(f"   📈 Items in collection: {collection_count}")
                
                if collection_count > 0:
                    # Test a simple query
                    test_results = self.collection.query(
                        query_texts=["phone"],
                        n_results=3
                    )
                    print(f"   🔍 Test query found {len(test_results['ids'][0])} results")
                
            except Exception as e:
                print(f"   ❌ Verification error: {e}")
            
            return result
            
        except Exception as e:
            print(f"❌ Critical error during import: {str(e)}")
            return {"status": "error", "message": f"Critical error: {str(e)}"}

async def main():
    """Main function to run the import"""
    print("="*60)
    print("🚀 ChromaDB Product Import Script")
    print("="*60)
    
    importer = ChromaDBImporter()
    
    if not hasattr(importer, 'openai_client'):
        print("❌ Cannot proceed without OpenAI client")
        return
    
    result = await importer.import_products_to_chroma()
    
    print("\\n" + "="*60)
    print("📋 Final Result:")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
