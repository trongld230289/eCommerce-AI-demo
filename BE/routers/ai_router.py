from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from services.ai_service import AIService

router = APIRouter()

# Initialize AI service
ai_service = AIService()

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class SearchRequest(BaseModel):
    limit: Optional[int] = 10
    messages: List[Dict[str, str]]

class EmbedProductsResponse(BaseModel):
    status: str
    message: str
    total_products: Optional[int] = None

class SearchResponse(BaseModel):
    status: str
    function_used: Optional[str] = None  # "find_products" or "find_gifts"
    language_detected: Optional[str] = None
    search_intent: Optional[Dict[str, Any]] = None
    intro: Optional[str] = None  # Added intro field
    header: Optional[str] = None  # Added header field
    products: Optional[list] = None
    total_results: Optional[int] = None
    messages: Optional[List[Dict[str, str]]] = None  # Added messages for conversation

class VoiceSearchResponse(BaseModel):
    status: str
    transcribed_text: Optional[str] = None
    original_query_type: Optional[str] = None
    function_used: Optional[str] = None  # "find_products" or "find_gifts"
    language_detected: Optional[str] = None
    search_intent: Optional[Dict[str, Any]] = None
    intro: Optional[str] = None  # Added intro field
    header: Optional[str] = None  # Added header field
    products: Optional[list] = None
    total_results: Optional[int] = None
    messages: Optional[List[Dict[str, str]]] = None  # Added messages for conversation

@router.get("/ai/embed-products", response_model=EmbedProductsResponse)
async def embed_all_products():
    """
    Embed all products in the database and store in ChromaDB.
    This should be called whenever products are updated.
    """
    try:
        result = await ai_service.embed_all_products()
        return EmbedProductsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed products: {str(e)}")

@router.post("/ai/search", response_model=SearchResponse)
async def semantic_search(search_request: SearchRequest):
    """
    Perform intelligent semantic search using LangChain tools.
    Automatically determines whether to use find_products or find_gifts based on user intent.
    Supports conversation context and language detection.
    """
    try:
        result = await ai_service.semantic_search_middleware(
            messages=search_request.messages
            #update limit later
        )
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/ai/search")
async def semantic_search_get(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Perform intelligent semantic search using query parameter.
    Alternative GET endpoint for easier testing.
    """
    try:
        result = await ai_service.semantic_search_middleware(
            user_input=q, 
            conversation_context={"current_function": None, "messages": []}, 
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/ai/legacy-search", response_model=SearchResponse) 
async def legacy_semantic_search(search_request: SearchRequest):
    """
    Legacy semantic search endpoint using the original method.
    Use /ai/search for the new intelligent routing system.
    """
    try:
        result = await ai_service.semantic_search(
            user_input=search_request.query,
            limit=search_request.limit
        )
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/ai/search-by-voice", response_model=VoiceSearchResponse)
async def voice_search(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, m4a, etc.)"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Perform voice search on products:
    1. Transcribe audio to text using OpenAI Whisper
    2. Extract search intent from transcribed text
    3. Perform semantic search on products
    
    Supported audio formats: wav, mp3, m4a, flac, etc.
    Maximum file size: 25MB (OpenAI Whisper limit)
    """
    try:
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Check file size (25MB limit for Whisper)
        if audio.size and audio.size > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 25MB."
            )
        
        # Perform voice search (limit not needed anymore since middleware handles it)
        result = await ai_service.voice_search(audio.file)
        return VoiceSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice search failed: {str(e)}")

@router.post("/ai/extract-intent")
async def extract_search_intent(search_request: SearchRequest):
    """
    Extract search intent from user input using LLM.
    Useful for testing the intent extraction separately.
    """
    try:
        result = ai_service.extract_search_intent(search_request.query)
        return {"status": "success", "search_intent": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent extraction failed: {str(e)}")

@router.post("/ai/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Transcribe audio to text using OpenAI Whisper.
    Useful for testing transcription separately from search.
    
    Supported audio formats: wav, mp3, m4a, flac, etc.
    Maximum file size: 25MB (OpenAI Whisper limit)
    """
    try:
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Check file size (25MB limit for Whisper)
        if audio.size and audio.size > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 25MB."
            )
        
        # Transcribe audio
        result = ai_service.transcribe_audio(audio.file)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/ai/stats")
async def get_collection_stats():
    """
    Get statistics about the ChromaDB collection.
    """
    try:
        result = ai_service.get_collection_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/ai/health")
async def health_check():
    """
    Check if AI service is healthy and can connect to required services.
    """
    try:
        # Test ChromaDB connection
        stats = ai_service.get_collection_stats()
        
        # Test OpenAI connection by getting a simple embedding
        test_embedding = ai_service.get_embedding("test")
        
        return {
            "status": "healthy",
            "chromadb": "connected" if stats["status"] == "success" else "error",
            "openai": "connected" if test_embedding else "error",
            "collection_stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

class CategoryKeywordsResponse(BaseModel):
    status: str
    message: str
    categories: Optional[Dict[str, List[str]]] = None
    metadata: Optional[Dict[str, Any]] = None

@router.get("/ai/category-keywords", response_model=CategoryKeywordsResponse)
async def get_category_keywords():
    """
    Get the currently saved category keywords.
    
    Returns the keywords that were previously generated and saved to file.
    If no keywords file exists, returns empty results.
    
    Returns:
    - Current keywords grouped by category
    - Metadata about when keywords were generated
    """
    try:
        import json
        import os
        
        if not os.path.exists("category_keywords.json"):
            return CategoryKeywordsResponse(
                status="not_found",
                message="No category keywords file found. Use POST /ai/generate-category-keywords to create one.",
                categories={},
                metadata={}
            )
        
        with open("category_keywords.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        keywords_data = data.get("categories", {})
        metadata = {
            "generated_at": data.get("generated_at"),
            "total_categories": data.get("total_categories"),
            "product_count": data.get("product_count"),
            "model_used": data.get("model_used"),
            "version": data.get("version")
        }
        
        return CategoryKeywordsResponse(
            status="success",
            message=f"Retrieved keywords for {len(keywords_data)} categories",
            categories=keywords_data,
            metadata=metadata
        )
        
    except Exception as e:
        print(f"❌ Error in get_category_keywords endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve category keywords: {str(e)}")


class GenerateCategoryKeywordsResponse(BaseModel):
    status: str
    message: str
    categories_processed: int
    keywords_generated: Optional[Dict[str, List[str]]] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/ai/generate-category-keywords", response_model=GenerateCategoryKeywordsResponse)
async def generate_category_keywords(force: bool = Query(False, description="Force regeneration even if keywords exist")):
    """
    Generate keywords for all product categories using LLM.
    This endpoint:
    1. Queries the database for all unique categories (no duplicates)
    2. Uses LLM to generate relevant search keywords for each category
    3. Saves the generated keywords to category_keywords.json
    
    Args:
        force: If True, will regenerate keywords even if they already exist and are recent
    """
    try:
        # Import product service to access the database query functionality
        from product_service import product_service
        
        print(f"🚀 Starting category keywords generation (force={force})...")
        
        # Get all unique categories from database (this queries DB and removes duplicates)
        categories = product_service.get_categories()
        
        if not categories:
            return GenerateCategoryKeywordsResponse(
                status="error",
                message="No categories found in database",
                categories_processed=0
            )
        
        print(f"📂 Found {len(categories)} unique categories: {categories}")
        
        # Generate keywords using AI service
        success = ai_service.generate_and_save_category_keywords(categories, force=force)
        
        if success:
            # Read the generated keywords file to return the results
            import json
            import os
            
            if os.path.exists("category_keywords.json"):
                with open("category_keywords.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                keywords_data = data.get("categories", {})
                metadata = {
                    "generated_at": data.get("generated_at"),
                    "total_categories": data.get("total_categories"),
                    "product_count": data.get("product_count"),
                    "model_used": data.get("model_used"),
                    "version": data.get("version")
                }
                
                return GenerateCategoryKeywordsResponse(
                    status="success",
                    message=f"Successfully generated keywords for {len(categories)} categories",
                    categories_processed=len(categories),
                    keywords_generated=keywords_data,
                    metadata=metadata
                )
            else:
                return GenerateCategoryKeywordsResponse(
                    status="partial_success",
                    message="Keywords were generated but file not found",
                    categories_processed=len(categories)
                )
        else:
            return GenerateCategoryKeywordsResponse(
                status="error",
                message="Failed to generate category keywords",
                categories_processed=len(categories)
            )
            
    except Exception as e:
        print(f"❌ Error in generate_category_keywords endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate category keywords: {str(e)}")


@router.post("/ai/refresh-categories-and-keywords")
async def refresh_categories_and_keywords():
    """
    Refresh categories and generate keywords using the existing _dump_categories_to_json() function.
    This is a simpler endpoint that directly calls the existing functionality.
    """
    try:
        # Import product service 
        from product_service import product_service
        
        print("🔄 Refreshing categories and generating keywords...")
        
        # Call the existing function that queries DB and generates keywords
        product_service._dump_categories_to_json(generate_keywords=True)
        
        # Read the results
        import json
        import os
        
        categories_data = {}
        keywords_data = {}
        
        # Read categories file
        if os.path.exists("latest_categories.json"):
            with open("latest_categories.json", "r", encoding="utf-8") as f:
                categories_data = json.load(f)
        
        # Read keywords file  
        if os.path.exists("category_keywords.json"):
            with open("category_keywords.json", "r", encoding="utf-8") as f:
                keywords_data = json.load(f)
        
        return {
            "status": "success",
            "message": "Categories refreshed and keywords generated successfully",
            "categories": categories_data,
            "keywords_metadata": {
                "generated_at": keywords_data.get("generated_at"),
                "total_categories": keywords_data.get("total_categories"),
                "product_count": keywords_data.get("product_count"),
                "model_used": keywords_data.get("model_used"),
                "version": keywords_data.get("version")
            },
            "categories_count": len(categories_data) if isinstance(categories_data, list) else 0,
            "keywords_count": len(keywords_data.get("categories", {}))
        }
        
    except Exception as e:
        print(f"❌ Error in refresh_categories_and_keywords endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh categories and keywords: {str(e)}")
