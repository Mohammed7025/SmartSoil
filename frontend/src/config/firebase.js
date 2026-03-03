// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getDatabase } from "firebase/database";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDX5ReWQJaR_YCxA-3E5OFttNW6goQb9Nw",
    authDomain: "soilanalysis123.firebaseapp.com",
    databaseURL: "https://soilanalysis123-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "soilanalysis123",
    storageBucket: "soilanalysis123.firebasestorage.app",
    messagingSenderId: "666143383138",
    appId: "1:666143383138:web:4484043e828b668fe63b3b",
    measurementId: "G-Q9VVZWHRFZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Export services for use in the app
export const auth = getAuth(app);
export const db = getFirestore(app); // Firestore
export const rtdb = getDatabase(app); // Realtime Database

export default app;
