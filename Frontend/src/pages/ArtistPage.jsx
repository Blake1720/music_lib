import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import AlbumCard from "../components/AlbumCard";

const ArtistPage = () => {
  const { artistName } = useParams(); 
  const [albums, setAlbums] = useState([]);
  const [filteredAlbums, setFilteredAlbums] = useState([]);
  const [loading, setLoading] = useState(true);

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
        <h1 className="text-3xl font-bold mb-6">{artistName}</h1>

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
                image={`https://placehold.co/400x400?text=${album.name}`}
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
