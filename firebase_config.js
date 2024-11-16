// Import the necessary Firebase functions
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCJEu4stGTpHVIXG8Q2b3mYMFsjt4s9ybY",
  authDomain: "mango-disease-detection.firebaseapp.com",
  projectId: "mango-disease-detection",
  storageBucket: "mango-disease-detection.appspot.com",
  messagingSenderId: "218043021587",
  appId: "1:218043021587:web:80b935447a26bd189f82e6",
  measurementId: "G-GLQM6NK5RS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
