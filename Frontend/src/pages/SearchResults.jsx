import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import SongCard from "../components/SongCard";
import ArtistCard from "../components/ArtistCard";
import AlbumCard from "../components/AlbumCard";
import { auth } from "../firebase";
import ConfirmModal from "../components/GenerateModal";
const SearchResults = () => {
  const { search } = useLocation(); // ?q=...
  const query = new URLSearchParams(search).get("q") || "";
  const [results, setResults] = useState({ artists: [], albums: [], songs: [] });
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
        throw new Error("Failed to generate playlist");
      }
  
      const result = await response.json();
      console.log("Playlist created!", result);
  
    } catch (error) {
      console.error("Error generating playlist:", error.message);
    } finally {
      setShowModal(false);
      setSelectedItem(null);
    }
  };
  useEffect(() => {
    const fetchSearchResults = async () => {
      try {
        const res = await fetch(`http://localhost:8000/database/search?q=${encodeURIComponent(query)}`);
        if (!res.ok) throw new Error("Failed to fetch search results");

        const data = await res.json();
        setResults({
          artists: data.artists || [],
          albums: data.albums || [],
          songs: data.songs || [],
        });
      } catch (err) {
        console.error("Error fetching search results:", err.message);
      } finally {
        setLoading(false);
      }
    };

    if (query) {
      fetchSearchResults();
    }
  }, [query]);

  return (
    <div className="flex justify-center min-h-screen text-white px-4 py-10">
      <div className="w-full max-w-7xl">
        {/* Modal */}
        {showModal && (
          <ConfirmModal
            title={`Generate playlist for ${selectedItem.title}?`}
            onConfirm={handleGenerate}
            onCancel={handleCloseModal}
          />
        )}
        <h1 className="text-3xl font-bold mb-8">
          Search Results for "{query}"
        </h1>

        {/* Songs */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Songs</h2>
          {results.songs.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-8">
              {results.songs.map((song) => (
                <SongCard
                  onCardClick={handleCardClick}
                  key={song.id}
                  id={song.id}
                  title={song.name}
                  artist={song.artist}
                  image={song.image || `https://placehold.co/400x400?text=${song.name}`}
                />
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">No matching songs.</p>
          )}
        </section>

        {/* Artists */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Artists</h2>
          {results.artists.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-8">
              {results.artists.map((artist) => (
                <ArtistCard
                  key={artist.id}
                  id={artist.id}
                  name={artist.name}
                  image={artist.image || "https://placehold.co/400x400?text=Artist"}
                />
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">No matching artists.</p>
          )}
        </section>

        {/* Albums */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Albums</h2>
          {results.albums.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-8">
              {results.albums.map((album) => (
                <AlbumCard
                  key={album.id}
                  id={album.id}
                  name={album.name}
                  artist={album.artist}
                  image={album.image || `https://placehold.co/400x400?text=${encodeURIComponent(album.name)}`}
                />
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">No matching albums.</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default SearchResults;
