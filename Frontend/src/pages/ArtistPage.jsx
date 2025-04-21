import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import AlbumCard from "../components/AlbumCard";
import { auth } from "../firebase";
import ConfirmModal from "../components/GenerateModal";

const ArtistPage = () => {
  const { artistName } = useParams(); 
  const [albums, setAlbums] = useState([]);
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = auth.currentUser;
  const username = user?.displayName;
  const [showModal, setShowModal] = useState(false);
  
  const handleCardClick = (item) => {
    setShowModal(true);
  };
  
  const handleCloseModal = () => {
    setShowModal(false);
  };
  
  const handleGenerate = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/artists/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          artist_name: `${artistName}`,
          name: `${artistName}`,
          limit: 10,
        }),
      });
  
      if (!response.ok) {
        throw new Error("Failed to generate playlist");
      }
  
      const result = await response.json();
      alert(`Playlist created successfully!`);
  
    } catch (error) {
      alert(`Playlist already exists!`);
    } finally {
      setShowModal(false);
    }
  };
  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const res = await fetch("http://localhost:8000/database/albums");
        if (!res.ok) throw new Error("Failed to fetch albums");

        const data = await res.json();
        setAlbums(data.albums || []);
      } catch (err) {
        console.error("Error fetching albums:", err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAlbums();
  }, []);

  useEffect(() => {
    if (artistName && albums.length > 0) {
      const matches = albums.filter(
        (album) => album.artist.toLowerCase() === artistName.toLowerCase()
      );
      setFilteredAlbums(matches);
    }
  }, [artistName, albums]);

  return (
    <div className="min-h-screen text-white px-6 py-10 bg-neutral-950">
      <div className="max-w-7xl mx-auto">
        {/* Modal */}
        {showModal && (
          <ConfirmModal
            title={`Generate playlist for ${artistName}?`}
            onConfirm={handleGenerate}
            onCancel={handleCloseModal}
          />
        )}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">{artistName}</h1>
          <button
            onClick={() => handleCardClick({ name: artistName })}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition"
          >
            Generate Playlist
          </button>
        </div>

        {loading ? (
          <p className="text-zinc-400">Loading...</p>
        ) : filteredAlbums.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-6">
            {filteredAlbums.map((album) => (
              <AlbumCard
                key={album.id}
                id={album.id}
                name={album.name}
                artist={album.artist}
                image={album.url || `/album_cover.jpg`}
              />
            ))}
          </div>
        ) : (
          <p className="text-zinc-500">No albums found for this artist.</p>
        )}
      </div>
    </div>
  );
};

export default ArtistPage;
