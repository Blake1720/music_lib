import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebase";

const PlaylistCard = ({ id, name, description, image, url }) => {
  const [clicked, setClicked] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const navigate = useNavigate();
  const username = auth.currentUser?.displayName;

  const handleClick = () => {
    if (clicked) {
      navigate(url);
    } else {
      setClicked(true);
      setTimeout(() => setClicked(false), 1000);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent navigation when clicking delete
    if (!username || isDeleting) return;

    setIsDeleting(true);
    try {
      const response = await fetch(
        `http://localhost:8000/database/playlists?username=${encodeURIComponent(username)}&playlist_name=${encodeURIComponent(name)}`,
        { method: "DELETE" }
      );
      
      if (!response.ok) throw new Error("Failed to delete playlist");
      
      // Refresh the page to update the playlist list
      window.location.reload();
    } catch (error) {
      console.error("Error deleting playlist:", error);
      alert("Failed to delete playlist. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`w-full bg-neutral-900 hover:bg-neutral-800 cursor-pointer p-1 rounded-lg shadow-md border transition duration-200 flex flex-row gap-4 items-center justify-between ${
        clicked ? "border-green-400" : "border-transparent"
      }`}
    >
      <div className="flex flex-row gap-4 items-center">
        <img
          src={image}
          alt={name}
          className="w-16 h-16 rounded-md object-cover"
          onError={(e) => (e.target.src = "https://placehold.co/64x64")}
        />
        <div>
          <h2 className="text-sm font-semibold text-white truncate">{name}</h2>
        </div>
      </div>
      <button
        onClick={handleDelete}
        disabled={isDeleting}
        className="p-2 text-red-500 hover:text-red-400 transition-colors"
        title="Delete playlist"
      >
        {isDeleting ? (
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        ) : (
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default PlaylistCard;
