# E-Commerce AI Demo Frontend

A modern e-commerce React application built with TypeScript, Firebase, and Tailwind CSS. This project demonstrates a complete shopping experience with authentication, product browsing, cart management, and wishlist functionality.

## 🚀 Quick Start

### Option 1: Convenient Startup (Recommended)
```bash
python run_FE.py
```

### Option 2: Batch File (Windows)
```bash
run_FE.bat
```

### Option 3: Standard npm
```bash
npm install
npm start
```

## 🎯 Features

- **User Authentication**: Login and registration with Firebase Auth
- **Product Catalog**: Browse and search products with semantic search
- **Shopping Cart**: Add/remove items with quantity management
- **Wishlist System**: Save favorite products with full CRUD operations
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **Real-time Updates**: Firebase Firestore integration
- **TypeScript**: Type-safe development experience
- **Hot Reload**: Instant updates during development

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript
- **Styling**: Tailwind CSS, PostCSS
- **Icons**: FontAwesome, Heroicons
- **Routing**: React Router DOM
- **Backend Integration**: Firebase (Authentication & Firestore)
- **Build Tool**: Create React App with TypeScript template
- **Development**: Hot reload, ESLint, TypeScript compiler

## 📋 Prerequisites

Before running this project, make sure you have the following installed:

- **Node.js** (version 16.0 or higher)
- **npm** or **yarn** package manager
- **Python** (for convenient startup script)
- **Firebase account** for backend services

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/trongld230289/eCommerce-AI-demo.git
cd eCommerce-AI-demo/FE
```

### 2. Install Dependencies

```bash
npm install
```

or if you prefer yarn:

```bash
yarn install
```

## 🚀 Running the Application

### Method 1: Smart Python Launcher (Recommended)
The `run_FE.py` script provides automatic setup and enhanced startup:

```bash
python run_FE.py
```

**Features:**
- ✅ Automatic Node.js and npm version checking
- ✅ Dependency installation if needed
- ✅ Port availability checking
- ✅ Process cleanup
- ✅ Backend connection verification
- ✅ Colored console output
- ✅ Error handling and recovery

### Method 2: Windows Batch File
For Windows users who prefer batch files:

```bash
run_FE.bat
```

**Features:**
- ✅ Basic dependency checking
- ✅ Automatic npm install
- ✅ Process cleanup
- ✅ Simple startup

### Method 3: Standard npm
Traditional npm approach:

```bash
npm start
```

### Method 4: Development Options
```bash
# Start with specific port
npm start -- --port 3001

# Start without opening browser
BROWSER=none npm start

# Start with custom environment
REACT_APP_API_URL=http://localhost:8000 npm start
```

## 📱 Access the Application

Once started, the application will be available at:
- **Local**: http://localhost:3000
- **Network**: http://your-ip:3000 (for testing on mobile devices)

The development server includes:
- 🔥 **Hot reload** for instant updates
- 🔍 **TypeScript checking**
- 🧹 **ESLint integration**
- 📱 **Mobile responsive design**

### 3. Firebase Configuration

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use an existing one
3. Enable **Authentication** and **Firestore Database**
4. Get your Firebase configuration from Project Settings
5. Update the Firebase configuration in `src/utils/firebase.ts`:

```typescript
const firebaseConfig = {
  apiKey: "your-actual-api-key",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};
```

### 4. Environment Variables (Optional)

For better security, you can use environment variables. Create a `.env` file in the root directory:

```env
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
```

Then update `firebase.ts` to use these variables.

## 🚀 Running the Project

### Development Mode

To start the development server:

```bash
npm start
```

or

```bash
yarn start
```

The application will open in your browser at `http://localhost:3000`

### Production Build

To create a production build:

```bash
npm run build
```

or

```bash
yarn build
```

The build files will be generated in the `build/` directory.

### Testing

To run tests:

```bash
npm test
```

or

```bash
yarn test
```

## 📁 Project Structure

```
eCommerce-AI-demo/
├── public/
│   └── index.html
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── AuthContext.tsx
│   │   ├── Cart.tsx
│   │   ├── CartDropdown.tsx
│   │   ├── Login.tsx
│   │   ├── LoginDialog.tsx
│   │   ├── Products.tsx
│   │   ├── Register.tsx
│   │   ├── SearchBar.tsx
│   │   ├── ShopContext.tsx
│   │   ├── SimpleProductCard.tsx
│   │   └── Wishlist.tsx
│   ├── contexts/            # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── ShopContext.tsx
│   ├── pages/               # Page components
│   │   ├── Cart.tsx
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Products.tsx
│   │   ├── Register.tsx
│   │   └── Wishlist.tsx
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/               # Utility functions
│   │   ├── firebase.ts
│   │   ├── mockData.ts
│   │   └── searchParser.ts
│   ├── App.tsx              # Main application component
│   ├── index.tsx            # Application entry point
│   └── index.css            # Global styles
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 🎯 Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Runs the app in development mode |
| `npm run build` | Builds the app for production |
| `npm test` | Launches the test runner |
| `npm run eject` | Ejects from Create React App (one-way operation) |

## 🔥 Firebase Setup Guide

### Authentication Setup
1. In Firebase Console, go to Authentication > Sign-in method
2. Enable Email/Password authentication
3. Configure authorized domains if needed

### Firestore Database Setup
1. Go to Firestore Database in Firebase Console
2. Create database in test mode (or production mode with proper rules)
3. Create collections for:
   - `products` - Store product information
   - `users` - Store user profiles
   - `carts` - Store shopping cart data
   - `wishlists` - Store wishlist data

## 🎨 Customization

### Styling
- Modify `tailwind.config.js` to customize the design system
- Update `src/index.css` for global styles
- Components use Tailwind utility classes for styling

### Adding New Features
1. Create new components in `src/components/`
2. Add new pages in `src/pages/`
3. Update routing in `src/App.tsx`
4. Add TypeScript types in `src/types/`

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Configuration Error**
   - Ensure all Firebase config values are correct
   - Check if Firebase services are enabled

2. **Build Fails**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for TypeScript errors

3. **Authentication Issues**
   - Verify Firebase Auth is properly configured
   - Check browser console for detailed error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- [Demo](#) - Live demo (if available)
- [Firebase Documentation](https://firebase.google.com/docs)
- [React Documentation](https://reactjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 👨‍💻 Author

Created by [trongld230289](https://github.com/trongld230289)

---

**Happy Coding! 🚀**
