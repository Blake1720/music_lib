import '../App.css';
import SongCard from '../components/SongCard';
import { useState, useEffect } from 'react';
import { auth } from "../firebase";
import ConfirmModal from "../components/GenerateModal";


const Home = () => {
  const [spotifyLink, setSpotifyLink] = useState("");
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [songSort, setSongSort] = useState(null);
  const user = auth.currentUser;
  const username = user?.displayName;
  const [selectedItem, setSelectedItem] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  const handleCardClick = (item) => {
    setSelectedItem(item);
    setShowModal(true);
  };
  
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedItem(null);
  };
  
  const handleGenerate = async () => {
    if (!selectedItem || !selectedItem.id) {
      console.error("No song selected.");
      return;
    }
  
    try {
      const response = await fetch(`http://localhost:8000/api/v1/songs/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          song_id: selectedItem.id,
          name: `${selectedItem.title || selectedItem.name}`,
        }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate playlist");
      }
  
      const result = await response.json();
      alert(`Playlist "${result.playlist.name}" created successfully!`);
  
    } catch (error) {
      console.error("Error generating playlist:", error);
      alert(error.message || "Failed to create playlist. Please try again.");
    } finally {
      setShowModal(false);
      setSelectedItem(null);
    }
  };
  
  useEffect(() => {
    const fetchSongs = async () => {
      try {
        let url = "http://localhost:8000/database/songs";
        if (songSort) {
          url += `?sort_by=${songSort}`;
        }
        
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch songs");

        const data = await res.json();
        setSongs(data.songs || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSongs();
  }, [songSort]);

  const handleAddSong = async () => {
    if (spotifyLink.trim() === "") return;
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/spotify/import", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          spotify_url: spotifyLink,
        }),
      });
  
      if (!response.ok) throw new Error("Failed to import song.");
  
      const result = await response.json();
      console.log("Song imported:", result.song_id);
  
      // Refresh song list
      const songList = await fetch("http://127.0.0.1:8000/database/songs");
      const data = await songList.json();
      setSongs(data.songs);
  
      setSpotifyLink("");
    } catch (error) {
      console.error("Error:", error.message);
    }
  };
  
  if (loading) return <div className="text-white text-center">Loading...</div>;
  if (error) return <div className="text-red-500 text-center">Error: {error}</div>;

  return (
    <div className="min-h-screen text-white px-4 py-10 flex justify-center bg-[linear-gradient(300deg,_#22c55e_30%,_#000_70%)]">
      <div className="w-full max-w-7xl">
        {/* Modal */}
        {showModal && (
          <ConfirmModal
            title={`Generate playlist for ${selectedItem.title}?`}
            onConfirm={handleGenerate}
            onCancel={handleCloseModal}
          />
        )}
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Your Music Dashboard
          </h1>
          <p className="text-zinc-400 mt-2 text-sm md:text-base">
            Add songs and explore your favorites
          </p>
        </div>

        {/* Add Song Input */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <input
            type="text"
            value={spotifyLink}
            onChange={(e) => setSpotifyLink(e.target.value)}
            placeholder="Paste Spotify link here"
            className="w-full sm:w-96 px-4 py-2 rounded-lg bg-neutral-800 text-white placeholder:text-zinc-400 focus:outline-none"
          />
          <button
            onClick={handleAddSong}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
          >
            Add Song
          </button>
        </div>

        {/* Songs Section */}
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-6 text-left">
            Songs
          </h2>
          <select
            value={songSort || ""}
            onChange={(e) => setSongSort(e.target.value || null)}
            className="bg-neutral-800 text-white px-3 py-1 rounded-lg"
          >
            <option value="">Sort by ID</option>
            <option value="name_asc">A to Z</option>
            <option value="name_desc">Z to A</option>
          </select>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-8">
          {songs.map((song) => (
            <SongCard
              onCardClick={handleCardClick}
              key={song.id}
              id={song.id}
              title={song.name}
              artist={song.artist}
              image={song.image}
              album_url={song.album_url}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
