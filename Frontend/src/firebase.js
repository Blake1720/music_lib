// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCjW7fWeIOJDJoJw3r_5UWhzV85mPvT-a0",
  authDomain: "musiclib-ab953.firebaseapp.com",
  projectId: "musiclib-ab953",
  storageBucket: "musiclib-ab953.firebasestorage.app",
  messagingSenderId: "89175259442",
  appId: "1:89175259442:web:ca45315db2ca5813adbf2b",
  measurementId: "G-TCGPYLCWR7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);