import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

function NavBar() {
  const user = auth.currentUser;
  const username = user?.displayName;
  const navigate = useNavigate();

  const [query, setQuery] = useState(""); // ✅ hold the input value

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim() !== "") {
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <nav className="bg-neutral-900 text-white px-6 py-4 flex flex-col md:flex-row md:justify-between md:items-center gap-4 shadow-md">
      {/* Left Side: Logo + Username */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <div className="text-2xl font-bold tracking-tight">
          Music<span className="text-green-400">Lib</span>
        </div>

        {username && (
          <h1 className="text-sm font-medium text-zinc-300 mt-2">
            Welcome, <span className="text-green-400 font-semibold">{username}</span>
          </h1>
        )}
      </div>

      {/* Search Bar + Button */}
      <form className="flex items-center gap-4" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search"
          value={query}
          onChange={(e) => setQuery(e.target.value)} // ✅ update query state
          className="bg-neutral-800 text-white px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition"
        />
        <button
          type="submit"
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md font-medium transition"
        >
          Search
        </button>
      </form>
    </nav>
  );
}

export default NavBar;
