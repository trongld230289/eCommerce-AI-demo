from fastapi import APIRouter, HTTPException, Query, UploadFile, File
<<<<<<< HEAD
from typing import Dict, Any, Optional
=======
from typing import Dict, Any, Optional, List
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
from pydantic import BaseModel

from services.ai_service import AIService

router = APIRouter()

# Initialize AI service
ai_service = AIService()

<<<<<<< HEAD
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
=======
class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class SearchRequest(BaseModel):
    limit: Optional[int] = 10
    messages: List[Dict[str, str]]
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

class EmbedProductsResponse(BaseModel):
    status: str
    message: str
    total_products: Optional[int] = None

class SearchResponse(BaseModel):
    status: str
<<<<<<< HEAD
    search_intent: Optional[Dict[str, Any]] = None
    products: Optional[list] = None
    total_results: Optional[int] = None
    message: Optional[str] = None
=======
    function_used: Optional[str] = None  # "find_products" or "find_gifts"
    language_detected: Optional[str] = None
    search_intent: Optional[Dict[str, Any]] = None
    intro: Optional[str] = None  # Added intro field
    header: Optional[str] = None  # Added header field
    show_all_product: Optional[str] = None  # Added show_all_product field
    products: Optional[list] = None
    total_results: Optional[int] = None
    messages: Optional[List[Dict[str, str]]] = None  # Added messages for conversation
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

class VoiceSearchResponse(BaseModel):
    status: str
    transcribed_text: Optional[str] = None
<<<<<<< HEAD
    search_intent: Optional[Dict[str, Any]] = None
    products: Optional[list] = None
    total_results: Optional[int] = None
    original_query_type: Optional[str] = None
    message: Optional[str] = None

@router.post("/ai/embed-products", response_model=EmbedProductsResponse)
=======
    original_query_type: Optional[str] = None
    function_used: Optional[str] = None  # "find_products" or "find_gifts"
    language_detected: Optional[str] = None
    search_intent: Optional[Dict[str, Any]] = None
    intro: Optional[str] = None  # Added intro field
    header: Optional[str] = None  # Added header field
    show_all_product: Optional[str] = None  # Added show_all_product field
    products: Optional[list] = None
    total_results: Optional[int] = None
    messages: Optional[List[Dict[str, str]]] = None  # Added messages for conversation

@router.get("/ai/embed-products", response_model=EmbedProductsResponse)
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
    Perform semantic search on products using natural language query.
    The AI will extract search intent and apply appropriate filters.
    """
    try:
        result = await ai_service.semantic_search(
            user_input=search_request.query,
            limit=search_request.limit
=======
    Perform intelligent semantic search using LangChain tools.
    Automatically determines whether to use find_products or find_gifts based on user intent.
    Supports conversation context and language detection.
    """
    try:
        result = await ai_service.semantic_search_middleware(
            messages=search_request.messages
            #update limit later
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
    Perform semantic search on products using query parameter.
    Alternative GET endpoint for easier testing.
    """
    try:
        result = await ai_service.semantic_search(user_input=q, limit=limit)
=======
    Perform intelligent semantic search using query parameter.
    Alternative GET endpoint for easier testing.
    """
    try:
        result = await ai_service.semantic_search_middleware(
            messages=[{"role": "user", "content": q}]
        )
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

<<<<<<< HEAD
=======
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

>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
        
<<<<<<< HEAD
        # Perform voice search
        result = await ai_service.voice_search(audio.file, limit)
=======
        # Perform voice search (limit not needed anymore since middleware handles it)
        result = await ai_service.voice_search(audio.file)
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
