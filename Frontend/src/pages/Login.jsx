import React, { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { Link, useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, pass);
      const username = userCredential.user.displayName;
      
      // Create user in our database if they don't exist
      const response = await fetch("http://localhost:8000/account/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: username,
          age: null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status !== 409) { // 409 is "user already exists"
          throw new Error(errorData.detail || "Failed to create user in database");
        }
      }
      
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="w-full max-w-sm bg-neutral-900 p-8 rounded-xl shadow-lg"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Log in</h2>
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          className="w-full p-3 mb-4 bg-neutral-800 rounded-md outline-none"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-3 mb-6 bg-neutral-800 rounded-md outline-none"
          value={pass}
          onChange={(e) => setPass(e.target.value)}
        />
        <button
          type="submit"
          className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold p-3 rounded-md transition"
        >
          Log In
        </button>
        <p className="mt-4 text-center text-sm text-zinc-400">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="text-green-400 cursor-pointer hover:underline"
          >
            Sign up
          </Link>
        </p>
      </form>
    </div>
  );
};

export default Login;
