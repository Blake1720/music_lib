import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import SongList from "../components/SongList";

const AlbumPage = () => {
  const { albumId } = useParams();
  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const response = await fetch(`http://localhost:8000/database/albums/${albumId}/songs`);
        if (!response.ok) throw new Error("Failed to fetch albums");

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

  if (loading) {
    return <div className="text-white p-10">Loading album...</div>;
  }

  if (!album) {
    return <div className="text-white p-10">Album not found.</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">
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
        <SongList songs={album.songs} />
      </div>
    </div>
  );
};

export default AlbumPage;
