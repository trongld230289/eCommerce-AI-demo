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
