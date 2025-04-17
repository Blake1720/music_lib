import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { auth } from "../firebase";
import SongList from "../components/SongList";

const PlaylistPage = () => {
  const { playlistName } = useParams();
  const user = auth.currentUser;
  const username = user?.displayName;
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [playlistInfo, setPlaylistInfo] = useState(null);

  useEffect(() => {
    const fetchSongs = async () => {
      if (!username) return;

      try {
        const res = await fetch(
          `http://localhost:8000/database/playlists/songs?username=${encodeURIComponent(
            username
          )}&playlist_name=${encodeURIComponent(playlistName)}`
        );
        if (!res.ok) throw new Error("Failed to fetch playlist songs");
        const data = await res.json();
        setSongs(data);
        setPlaylistInfo({
          name: playlistName,
          image: `https://placehold.co/100x100?text=${playlistName}`,
        });
      } catch (err) {
        console.error("Error loading playlist:", err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSongs();
  }, [playlistName, username]);

  if (loading) {
    return <div className="text-white p-10">Loading playlist...</div>;
  }

  if (!playlistInfo) {
    return <div className="text-white p-10">Playlist not found.</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-6 mb-10">
          <img
            src={playlistInfo.image}
            alt={playlistInfo.name}
            className="w-32 h-32 object-cover rounded-lg"
          />
          <div>
            <h1 className="text-3xl font-bold">{playlistInfo.name}</h1>
          </div>
        </div>

        {/* Song List */}
        <SongList songs={songs} />
      </div>
    </div>
  );
};

export default PlaylistPage;
