// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore"; // 이 줄이 반드시 필요!
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBNLymEnzJII78w6XXGHL-UXXdd5vnjLNs",
  authDomain: "recyleme-423ce.firebaseapp.com",
  projectId: "recyleme-423ce",
  storageBucket: "recyleme-423ce.firebasestorage.app",
  messagingSenderId: "994538493842",
  appId: "1:994538493842:web:97392de82dfcfacc8d134b",
  measurementId: "G-1SK8ZFV4JV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const db = getFirestore(app); // <-- Add this