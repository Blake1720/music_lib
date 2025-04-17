import { useEffect, useState } from "react";
import { auth } from "../firebase";
import PlaylistCard from "../components/PlaylistCard";

const Playlists = () => {
  const [playlists, setPlaylists] = useState([]);
  const username = auth.currentUser?.displayName;

  useEffect(() => {
    const fetchPlaylists = async () => {
      if (!username) return;

      try {
        const response = await fetch(`http://localhost:8000/database/playlists?username=${encodeURIComponent(username)}`);
        if (!response.ok) throw new Error("Failed to fetch playlists");

        const data = await response.json();
        const enriched = data.playlists.map((p, index) => ({
          id: index.toString(),
          name: p.name,
          description: `${p.song_count} song(s)`,
          image: `https://placehold.co/100x100?text=${encodeURIComponent(p.name)}`,
          url: `/playlists/${p.name}`
        }));

        setPlaylists(enriched);
      } catch (err) {
        console.error("Error loading playlists:", err.message);
      }
    };

    fetchPlaylists();
  }, [username]);

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-bold mb-8">Your Playlists</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard key={playlist.id} {...playlist} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Playlists;