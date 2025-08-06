import { initializeApp } from 'firebase/app';
import { getAuth, Auth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore, Firestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyAvKhYTDmcQCCqHB-FangSOfNNldRoQumg",
  authDomain: "ecommerce-ai-cfafd.firebaseapp.com",
  projectId: "ecommerce-ai-cfafd",
  storageBucket: "ecommerce-ai-cfafd.appspot.com",
  messagingSenderId: "371226329624",
  appId: "1:371226329624:web:8402f66ab30f213cd7f96d",
  measurementId: "G-E1C8VEV5CS"
};

// Initialize Firebase
let app;
let auth: Auth;
let db: Firestore;

try {
  app = initializeApp(firebaseConfig);
  
  // Initialize Firebase Authentication and get a reference to the service
  auth = getAuth(app);
  
  // Initialize Cloud Firestore and get a reference to the service
  db = getFirestore(app);
  
  console.log('Firebase initialized successfully');
  console.log('Project ID:', firebaseConfig.projectId);
  console.log('Auth Domain:', firebaseConfig.authDomain);
  
  // Validate Firebase configuration
  if (!firebaseConfig.apiKey || !firebaseConfig.authDomain || !firebaseConfig.projectId) {
    throw new Error('Firebase configuration is incomplete');
  }
  
} catch (error) {
  console.error('Error initializing Firebase:', error);
  console.error('Please check:');
  console.error('1. Firebase project configuration is correct');
  console.error('2. Email/Password authentication is enabled in Firebase Console');
  console.error('3. Google authentication is enabled in Firebase Console (if using Google sign-in)');
  console.error('4. Authorized domains include your localhost/domain');
  throw error;
}

export { auth, db };
export default app;

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});
