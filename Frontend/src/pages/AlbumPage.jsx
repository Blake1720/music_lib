import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { auth } from "../firebase";
import ConfirmModal from "../components/GenerateModal";
import SongList from "../components/SongList";

const AlbumPage = () => {
  const { albumId } = useParams();
  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);
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

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const response = await fetch(`http://localhost:8000/database/albums/${albumId}/songs`);
        if (!response.ok) throw new Error("Failed to fetch album");

        const data = await response.json();
        setAlbum(data || null);
      } catch (error) {
        console.error("Error loading album:", error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAlbums();
  }, [albumId]);

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

  if (loading) return <div className="text-white p-10">Loading album...</div>;
  if (!album) return <div className="text-white p-10">Album not found.</div>;

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
            src={album.url || "https://placehold.co/400x400?text=Album"}
            alt={album.name}
            className="w-32 h-32 object-cover rounded-lg"
          />
          <div>
            <h1 className="text-3xl font-bold">{album.name}</h1>
            <p className="text-zinc-400 mt-1 text-sm">by {album.artist}</p>
          </div>
        </div>

        {/* Song List */}
        <SongList songs={album.songs} onCardClick={handleCardClick} />
      </div>
    </div>
  );
};

export default AlbumPage;
