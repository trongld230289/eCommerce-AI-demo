# eCommerce AI - Full Stack Application

A modern full-stack eCommerce application with React frontend, Python backend, and Firebase integration. Features AI-powered recommendations, product search, and comprehensive product management.

## 🏗️ Architecture

```
eCommerce-AI/
├── FE/              # React Frontend (TypeScript)
├── BE/              # Python Backend (FastAPI + Firebase)
├── AI_Service/      # AI Recommendation Service
└── docs/            # Documentation
```

## 🚀 Features

### Frontend (React + TypeScript)
- **Modern UI**: Responsive design with Tailwind CSS
- **User Authentication**: Firebase Auth integration
- **Product Catalog**: Dynamic product browsing and search
- **Shopping Cart**: Full cart management with persistence
- **Wishlist**: Save favorite products
- **Real-time Updates**: Live inventory and price updates

### Backend (Python + FastAPI)
- **REST API**: Comprehensive product management APIs
- **Firebase Integration**: Firestore database for products
- **Search & Filtering**: Advanced product search with multiple filters
- **CORS Support**: Configured for frontend integration
- **API Documentation**: Automatic OpenAPI documentation

### AI Service
- **Recommendation Engine**: Personalized product recommendations
- **Chatbot Integration**: Natural language product search
- **User Preferences**: Learning from user behavior

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Firebase SDK** for authentication
- **FontAwesome** for icons

### Backend
- **FastAPI** for API framework
- **Firebase Admin SDK** for database operations
- **Pydantic** for data validation
- **Uvicorn** for ASGI server

### Database
- **Firebase Firestore** for product data
- **Firebase Auth** for user management

## 📋 Prerequisites

Before running this project, make sure you have:

- **Node.js** (version 16.0 or higher)
- **Python** (version 3.8 or higher)
- **npm** or **yarn** package manager
- **Firebase account** with a project set up

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/trongld230289/eCommerce-AI-demo.git
cd eCommerce-AI-demo
```

### 2. Firebase Setup

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing project `ecommerce-ai-cfafd`
3. Enable **Authentication** and **Firestore Database**
4. Create a service account key:
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Download the JSON file

### 3. Backend Setup

```bash
cd BE

# Install Python dependencies
pip install -r requirements.txt

# Configure Firebase
# Option 1: Place your Firebase service account JSON file in BE folder as 'firebase-service-account.json'
# Option 2: Set environment variables (see .env.example)

# Create .env file
cp .env.example .env
# Edit .env with your Firebase configuration

# Migrate data to Firebase
python migrate_data.py

# Start the backend server
python start.py
```

The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd FE

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
# Edit .env if needed (API URL is pre-configured)

# Start the frontend development server
npm start
```

The frontend will be available at: http://localhost:3000

### 5. AI Service (Optional)

```bash
cd AI_Service

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI/Azure OpenAI (if using AI features)
# Edit environment variables for AI service

# Start AI service
python main.py
```

## 🚀 Running the Application

### Quick Start (All Services)

1. **Start Backend:**
   ```bash
   cd BE && python start.py
   ```

2. **Start Frontend:**
   ```bash
   cd FE && npm start
   ```

3. **Start AI Service (Optional):**
   ```bash
   cd AI_Service && python main.py
   ```

### Development Mode

For development, you can run each service separately:

- **Backend**: `cd BE && uvicorn main:app --reload`
- **Frontend**: `cd FE && npm start`
- **AI Service**: `cd AI_Service && python main.py`

## 📁 Project Structure

```
eCommerce-AI/
├── FE/                          # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── contexts/            # React contexts (Auth, Shop, Toast)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript type definitions
│   │   └── utils/               # Utility functions
│   ├── package.json
│   └── tailwind.config.js
│
├── BE/                          # Python Backend
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── firebase_config.py       # Firebase configuration
│   ├── product_service.py       # Product business logic
│   ├── migrate_data.py          # Data migration script
│   ├── start.py                 # Startup script
│   ├── requirements.txt
│   └── README.md
│
├── AI_Service/                  # AI Recommendation Service
│   ├── main.py                  # FastAPI application
│   ├── chatbot_service.py       # Chatbot logic
│   ├── models.py                # Data models
│   ├── data.py                  # Sample data
│   └── requirements.txt
│
└── README.md                    # This file
```

## 🔗 API Endpoints

### Backend API (http://localhost:8000)

- `GET /products` - Get all products
- `GET /products/{id}` - Get product by ID
- `POST /products` - Create new product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `GET /search` - Search products with filters
- `GET /categories` - Get all categories
- `GET /brands` - Get all brands
- `GET /health` - Health check

### AI Service API (http://localhost:8000)

- `GET /recommendations` - Get personalized recommendations
- `POST /chatbot` - Process chatbot queries
- `GET /search` - AI-powered search

## 🔥 Firebase Configuration

### Firestore Collections

The application uses the following Firestore collections:

- **products**: Product catalog data
- **users**: User profiles (managed by Firebase Auth)
- **carts**: Shopping cart data (optional)
- **wishlists**: Wishlist data (optional)

### Security Rules

Make sure to configure appropriate Firestore security rules for production.

## 🎯 Key Features Implemented

### ✅ Completed
- [x] Python FastAPI backend with Firebase integration
- [x] Product CRUD operations via REST API
- [x] Data migration from hardcoded frontend data to Firebase
- [x] Frontend API integration with error handling and loading states
- [x] Search and filtering functionality
- [x] Responsive design and user authentication
- [x] Shopping cart and wishlist functionality

### 🔄 In Progress
- [ ] Enhanced AI recommendations
- [ ] Advanced search with machine learning
- [ ] Order management system
- [ ] Payment integration

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Configuration Error**
   - Ensure Firebase service account key is properly configured
   - Check if Firestore database is enabled
   - Verify project ID matches in configuration

2. **Backend Connection Issues**
   - Ensure backend is running on port 8000
   - Check CORS configuration if frontend can't connect
   - Verify environment variables are set correctly

3. **Frontend Build Fails**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for TypeScript errors
   - Ensure all dependencies are compatible

4. **Data Migration Issues**
   - Verify Firebase credentials
   - Check internet connection
   - Review Firebase console for error logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Trong Le** - [trongld230289](https://github.com/trongld230289)

## 🔗 Links

- **Repository**: https://github.com/trongld230289/eCommerce-AI-demo
- **Frontend Demo**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

⭐ If you find this project helpful, please give it a star!
