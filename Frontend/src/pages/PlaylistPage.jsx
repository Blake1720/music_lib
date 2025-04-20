import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { auth } from "../firebase";
import SongList from "../components/SongList";
import ConfirmModal from "../components/GenerateModal";

const PlaylistPage = () => {
  const { playlistName } = useParams();
  const user = auth.currentUser;
  const username = user?.displayName;
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [playlistInfo, setPlaylistInfo] = useState(null);
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

  const handleGenerate = async () => {
    if (!selectedItem || !selectedItem.id || !username) return;

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

      if (!response.ok) throw new Error("Failed to generate playlist");

      const result = await response.json();
      alert(`Playlist created successfully!`);
    } catch (error) {
      alert(`Playlist already exists!`);
    } finally {
      setShowModal(false);
      setSelectedItem(null);
    }
  };

  if (loading) {
    return <div className="text-white p-10">Loading playlist...</div>;
  }

  if (!playlistInfo) {
    return <div className="text-white p-10">Playlist not found.</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">
        {/* Modal */}
        {showModal && (
          <ConfirmModal
            title={`Generate playlist from "${selectedItem.title}"?`}
            onConfirm={handleGenerate}
            onCancel={handleCloseModal}
          />
        )}
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
        {songs.map((song) => (
            <SongList
              onCardClick={handleCardClick}
              key={song.id}
              id={song.id}
              title={song.name}
              artist={song.artist}
              image={`https://placehold.co/400x400?text=${song.name}`}
            />
        ))}
      </div>
    </div>
  );
};

export default PlaylistPage;
