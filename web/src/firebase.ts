import { initializeApp } from "firebase/app";
import { getAuth, Auth } from "firebase/auth";

// Check if we have real Firebase keys (not demo values)
const hasRealFirebaseKeys = import.meta.env.VITE_FIREBASE_API_KEY && 
  import.meta.env.VITE_FIREBASE_API_KEY !== 'demo-api-key';

let auth: Auth;

if (hasRealFirebaseKeys) {
  // Only initialize Firebase if we have real API keys
  const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  };

  try {
    const app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } catch (error) {
    console.warn('Firebase initialization failed:', error);
    auth = createMockAuth();
  }
} else {
  // Running in demo mode without Firebase
  console.log('Running in demo mode - Firebase authentication disabled');
  auth = createMockAuth();
}

function createMockAuth(): Auth {
  return {
    currentUser: null,
    onAuthStateChanged: () => () => {},
    signOut: () => Promise.resolve(),
  } as unknown as Auth;
}

export { auth };
