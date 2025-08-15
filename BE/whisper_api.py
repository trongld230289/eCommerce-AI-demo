from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import tempfile
import os
from dotenv import load_dotenv
import re


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

def detect_language(text):
    """Simple language detection for Vietnamese vs English"""
    # Basic detection: Vietnamese contains special characters
    vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]'
    return 'vi' if re.search(vietnamese_chars, text.lower()) else 'en'

def translate_to_english(text):
    """Translate Vietnamese text to English using GPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional translator. Translate the given Vietnamese text to English. Only respond with the English translation, no explanations or additional text."
                },
                {
                    "role": "user", 
                    "content": f"Translate this Vietnamese text to English: {text}"
                }
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Whisper API with Vietnamese Translation",
        "version": "2.0",
        "status": "running",
        "endpoints": {
            "/transcribe": "POST - Transcribe audio with optional translation",
            "/transcribe-and-translate": "POST - Transcribe and auto-translate Vietnamese",
            "/translate": "POST - Translate Vietnamese text to English",
            "/status": "GET - Service status"
        },
        "supported_languages": ["Vietnamese", "English"],
        "features": ["Speech-to-text", "Language detection", "Vietnamese→English translation"]
    })

@app.route("/status", methods=["GET"])
def status():
    """Service status endpoint"""
    try:
        # Quick test of OpenAI API
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        api_status = "healthy"
    except Exception as e:
        if "insufficient_quota" in str(e) or "rate_limit" in str(e).lower():
            api_status = "quota_exceeded"
        else:
            api_status = "error"
    
    return jsonify({
        "status": "running",
        "service": "Whisper API",
        "port": 5005,
        "openai_configured": bool(openai_api_key),
        "openai_api_status": api_status,
        "endpoints_available": ["/transcribe", "/transcribe-and-translate", "/translate"]
    })

@app.route("/check-quota", methods=["GET"])
def check_quota():
    """Check OpenAI API quota status"""
    try:
        # Small test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return jsonify({
            "quota_status": "available",
            "message": "OpenAI API is working normally"
        })
    except Exception as e:
        if "insufficient_quota" in str(e) or "rate_limit" in str(e).lower():
            return jsonify({
                "quota_status": "exceeded",
                "message": "OpenAI API quota exceeded",
                "error": str(e),
                "billing_url": "https://platform.openai.com/account/billing"
            }), 429
        else:
            return jsonify({
                "quota_status": "error",
                "message": "OpenAI API error",
                "error": str(e)
            }), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio to text, with optional translation"""
    print("📝 Transcribe endpoint called")
    
    if "audio" not in request.files:
        print("❌ No audio file in request")
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files["audio"]
    translate = request.form.get('translate', 'false').lower() == 'true'
    
    print(f"🎵 Audio file received: {audio_file.filename}, size: {len(audio_file.read())} bytes")
    audio_file.seek(0)  # Reset file pointer
    
    try:
        # Create temp file with original extension to preserve format info
        file_ext = ".wav"  # Default to wav
        if audio_file.content_type:
            if "webm" in audio_file.content_type:
                file_ext = ".webm"
            elif "mp4" in audio_file.content_type:
                file_ext = ".mp4"
            elif "mpeg" in audio_file.content_type:
                file_ext = ".mp3"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
            print(f"💾 Saved audio to temp file: {tmp_path} (content-type: {audio_file.content_type})")
        
        # Use OpenAI Whisper API with large-v2 model
        print("🔄 Calling OpenAI Whisper API...")
        with open(tmp_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # This uses the large-v2 model
                file=audio,
                response_format="text"
            )
        
        print(f"✅ Transcription successful: {transcript[:50]}...")
        os.unlink(tmp_path)
        
        result = {
            "text": transcript,
            "language": detect_language(transcript)
        }
        
        # If translation is requested and text is Vietnamese, translate it
        if translate and result["language"] == "vi":
            print("🌐 Translating Vietnamese to English...")
            translated_text = translate_to_english(transcript)
            result["translated_text"] = translated_text
            result["translation_available"] = True
        else:
            result["translation_available"] = False
        
        print(f"📤 Returning result: {result}")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Raw error in transcription: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
        # Return raw error without modification
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/transcribe-and-translate", methods=["POST"])
def transcribe_and_translate():
    """Transcribe audio and automatically translate Vietnamese to English"""
    print("🌐 Transcribe-and-translate endpoint called")
    
    if "audio" not in request.files:
        print("❌ No audio file in request")
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files["audio"]
    print(f"🎵 Audio file received: {audio_file.filename}, size: {len(audio_file.read())} bytes")
    audio_file.seek(0)  # Reset file pointer
    
    try:
        # Create temp file with original extension to preserve format info
        file_ext = ".wav"  # Default to wav
        if audio_file.content_type:
            if "webm" in audio_file.content_type:
                file_ext = ".webm"
            elif "mp4" in audio_file.content_type:
                file_ext = ".mp4"
            elif "mpeg" in audio_file.content_type:
                file_ext = ".mp3"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
            print(f"💾 Saved audio to temp file: {tmp_path} (content-type: {audio_file.content_type})")
        
        # Use OpenAI Whisper API with large-v2 model
        print("🔄 Calling OpenAI Whisper API...")
        with open(tmp_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # This uses the large-v2 model
                file=audio,
                response_format="text"
            )
        
        print(f"✅ Transcription successful: {transcript[:50]}...")
        os.unlink(tmp_path)
        
        detected_language = detect_language(transcript)
        print(f"🔍 Detected language: {detected_language}")
        
        result = {
            "original_text": transcript,
            "detected_language": detected_language
        }
        
        # Always translate if Vietnamese is detected
        if detected_language == "vi":
            print("🌐 Translating Vietnamese to English...")
            translated_text = translate_to_english(transcript)
            result["translated_text"] = translated_text
            result["final_text"] = translated_text  # Use translated text for AI processing
            print(f"✅ Translation: {translated_text[:50]}...")
        else:
            result["final_text"] = transcript  # Use original text if already English
            print("ℹ️ No translation needed - text is already in English")
        
        print(f"📤 Returning result with final_text: {result['final_text'][:50]}...")
        return jsonify(result)
    
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return jsonify({"error": f"Transcription and translation failed: {str(e)}"}), 500

@app.route("/translate", methods=["POST"])
def translate_text():
    """Translate Vietnamese text to English"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text']
    
    try:
        detected_language = detect_language(text)
        
        if detected_language == "vi":
            translated_text = translate_to_english(text)
            return jsonify({
                "original_text": text,
                "translated_text": translated_text,
                "detected_language": "vi"
            })
        else:
            return jsonify({
                "original_text": text,
                "translated_text": text,  # No translation needed
                "detected_language": "en",
                "message": "Text appears to be in English already"
            })
    
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5005, debug=True)
