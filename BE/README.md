# eCommerce AI Backend - Develop Branch 🚀

> **Branch**: `develop` | **Status**: Active Development  
> Advanced AI-powered eCommerce backend with intelligent product recommendations and conversational search.

## 🎯 Quick Start

### Activate Virtual Environment & Run
```bash
# Activate virtual environment
venv312\Scripts\activate

# Start the server
python run_BE.py
```

### Alternative Start Methods
```bash
# Direct FastAPI server
python main.py

# Full-featured server
python fastapi_server.py
```

## 🧠 AI Features (Develop Branch)

- **Intelligent Search**: Context-aware product search with smart category mapping
- **Conversational AI**: Natural language product recommendations  
- **Vector Database**: ChromaDB for semantic product matching
- **Smart Context Understanding**: Maps user intent to product categories
- **Multi-language Support**: Vietnamese, English, and more

## 🔧 Development Setup

### Prerequisites
```bash
# Ensure Python 3.12+ is installed
python --version

# Navigate to backend directory
cd BE
```

### Virtual Environment
```bash
# Activate environment
venv312\Scripts\activate

# Verify activation (Windows)
echo $env:VIRTUAL_ENV

# Install/Update dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL_ID=gpt-4o-mini
```

### Firebase Setup
1. Place `serviceAccountKey.json` in root directory
2. Initialize Firebase connection

## 🚀 Development Workflow

### 1. Environment Activation
```bash
# Always start with this
venv312\Scripts\activate
```

### 2. Server Launch
```bash
# Recommended for development
python run_BE.py

# Direct FastAPI (alternative)
uvicorn main:app --reload --port 8000
```

### 3. API Testing
- **Swagger UI**: http://localhost:8000/docs
- **AI Search**: http://localhost:8000/api/ai/search
- **Health Check**: http://localhost:8000/health

## 📡 Key API Endpoints

### AI & Search
- `POST /api/ai/search` - Intelligent product search
- `POST /api/ai/voice-search` - Voice-powered search
- `GET /api/ai/embed-products` - Initialize vector database

### Products & Recommendations  
- `GET /products` - All products
- `GET /recommendations` - Personalized suggestions
- `POST /events` - User activity tracking

### Wishlists & User Data
- `GET /api/wishlist` - User wishlists
- `POST /api/wishlist` - Create wishlist
- `POST /api/wishlist/{id}/products` - Add to wishlist

## 🎨 Development Notes

### Current Focus Areas
- Smart context understanding for search queries
- Enhanced conversation flow handling  
- Improved product recommendation algorithms
- Vector database optimization

### Debug Commands
```bash
# Test AI service directly
python -c "from services.ai_service import AIService; ai = AIService(); print('AI Service loaded')"

# Check database connection
python -c "from product_service import ProductService; ps = ProductService(); print(f'Products: {len(ps.get_all_products())}')"
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **AI Service Guide**: See `AI_SERVICE_README.md`


# my note (note change or remove)
# python -m services.product_relationship_service