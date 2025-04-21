import { useState, useEffect } from "react";
import { auth } from "../firebase";
import PlaylistCard from "../components/PlaylistCard";
import { useNavigate } from "react-router-dom";
import RenamePlaylistModal from "../components/RenamePlaylistModal";

const Playlists = () => {
  const [playlists, setPlaylists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameData, setRenameData] = useState(null);
  const [newName, setNewName] = useState("");
  const navigate = useNavigate();
  const user = auth.currentUser;
  const username = user?.displayName;

  useEffect(() => {
    console.log("Current user:", user);
    console.log("Username:", username);

    if (!user) {
      console.log("No user found, redirecting to login");
      navigate("/login");
      return;
    }

    if (!username) {
      console.log("No username found");
      setError("Please set a display name in your profile");
      setIsLoading(false);
      return;
    }

    const fetchPlaylists = async () => {
      try {
        console.log("Fetching playlists for username:", username);
        const response = await fetch(
          `http://localhost:8000/database/playlists?username=${encodeURIComponent(username)}`
        );
        
        if (!response.ok) {
          const errorData = await response.json();
          console.error("Error response:", errorData);
          throw new Error(errorData.detail || "Failed to fetch playlists");
        }
        
        const data = await response.json();
        console.log("Fetched playlists data:", data);
        
        // Extract playlists from the response object
        const playlistsArray = data.playlists || [];
        console.log("Processed playlists array:", playlistsArray);
        setPlaylists(playlistsArray);
      } catch (error) {
        console.error("Error fetching playlists:", error);
        setError(error.message || "Failed to load playlists");
        setPlaylists([]); // Set empty array on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlaylists();
  }, [user, username, navigate]);

  const handleRename = async (playlist) => {
    setRenameData(playlist);
    setNewName(playlist.name);
    setIsRenaming(true);
  };

  const handleRenameSubmit = async (newName) => {
    if (!newName.trim() || !renameData || !username) return;

    try {
      const response = await fetch(
        `http://localhost:8000/database/playlists/rename?username=${encodeURIComponent(username)}&old_name=${encodeURIComponent(renameData.name)}&new_name=${encodeURIComponent(newName)}`,
        { method: "PUT" }
      );

      if (!response.ok) throw new Error("Failed to rename playlist");

      setPlaylists(prevPlaylists =>
        prevPlaylists.map(playlist =>
          playlist.name === renameData.name
            ? { ...playlist, name: newName }
            : playlist
        )
      );

      setIsRenaming(false);
      setRenameData(null);
      setNewName("");
    } catch (error) {
      console.error("Error renaming playlist:", error);
      alert("Failed to rename playlist. Please try again.");
    }
  };

  if (isLoading) return <div className="text-white p-10">Loading playlists...</div>;
  if (error) return <div className="text-red-500 p-10">{error}</div>;

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Your Playlists</h1>
        {playlists.length === 0 ? (
          <div className="text-neutral-400 text-center py-10">
            No playlists found. Create a playlist by generating recommendations from a song or artist.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {playlists.map((playlist) => (
              <PlaylistCard
                key={playlist.name}
                id={playlist.name}
                name={playlist.name}
                description={playlist.description}
                image={playlist.image_url || `https://placehold.co/100x100?text=${playlist.name}`}
                url={`/playlists/${encodeURIComponent(playlist.name)}`}
                onRename={handleRename}
              />
            ))}
          </div>
        )}

        {isRenaming && (
          <RenamePlaylistModal
            isOpen={isRenaming}
            onClose={() => {
              setIsRenaming(false);
              setRenameData(null);
              setNewName("");
            }}
            playlistName={renameData?.name}
            onRename={handleRenameSubmit}
          />
        )}
      </div>
    </div>
  );
};

export default Playlists;