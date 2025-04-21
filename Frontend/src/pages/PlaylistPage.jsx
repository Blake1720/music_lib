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
  const [allSongs, setAllSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [playlistInfo, setPlaylistInfo] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showAddSongsModal, setShowAddSongsModal] = useState(false);
  const [selectedSongs, setSelectedSongs] = useState(new Set());
  const [isAddingSongs, setIsAddingSongs] = useState(false);
  
  const handleCardClick = (item) => {
    setSelectedItem(item);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedItem(null);
  };

  const handleAddSongsClick = () => {
    setShowAddSongsModal(true);
  };

  const handleCloseAddSongsModal = () => {
    setShowAddSongsModal(false);
    setSelectedSongs(new Set());
  };

  const handleSongSelect = (songId) => {
    setSelectedSongs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(songId)) {
        newSet.delete(songId);
      } else {
        newSet.add(songId);
      }
      return newSet;
    });
  };

  const handleAddSelectedSongs = async () => {
    if (selectedSongs.size === 0 || !username) return;

    setIsAddingSongs(true);
    try {
      const response = await fetch(
        `http://localhost:8000/database/playlists/songs?username=${encodeURIComponent(username)}&playlist_name=${encodeURIComponent(playlistName)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(Array.from(selectedSongs)),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to add songs to playlist");
      }

      // Refresh the playlist songs
      const res = await fetch(
        `http://localhost:8000/database/playlists/songs?username=${encodeURIComponent(username)}&playlist_name=${encodeURIComponent(playlistName)}`
      );
      if (!res.ok) throw new Error("Failed to fetch updated playlist");
      const data = await res.json();
      setSongs(data);

      handleCloseAddSongsModal();
    } catch (error) {
      console.error("Error adding songs:", error);
      alert("Failed to add songs to playlist. Please try again.");
    } finally {
      setIsAddingSongs(false);
    }
  };

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

  useEffect(() => {
    const fetchSongs = async () => {
      if (!username) return;

      try {
        // Fetch playlist songs
        const res = await fetch(
          `http://localhost:8000/database/playlists/songs?username=${encodeURIComponent(username)}&playlist_name=${encodeURIComponent(playlistName)}`
        );
        if (!res.ok) throw new Error("Failed to fetch playlist songs");
        const data = await res.json();
        setSongs(data);

        // Fetch all available songs
        const allSongsRes = await fetch("http://localhost:8000/database/songs");
        if (!allSongsRes.ok) throw new Error("Failed to fetch all songs");
        const allSongsData = await allSongsRes.json();
        setAllSongs(allSongsData.songs);

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
      <div className="max-w-7xl mx-auto">
        {playlistInfo && (
          <div className="flex items-center gap-6 mb-8">
            <img
              src={playlistInfo.image}
              alt={playlistInfo.name}
              className="w-32 h-32 rounded-lg object-cover"
            />
            <div>
              <h1 className="text-3xl font-bold">{playlistInfo.name}</h1>
              <p className="text-neutral-400 mt-2">{songs.length} songs</p>
              <button
                onClick={handleAddSongsClick}
                className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
              >
                Add Songs
              </button>
            </div>
          </div>
        )}

        <SongList songs={songs} onCardClick={handleCardClick} />

        {showModal && (
          <ConfirmModal
            title={`Generate playlist for ${selectedItem.title}?`}
            onConfirm={handleGenerate}
            onCancel={handleCloseModal}
          />
        )}

        {showAddSongsModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-neutral-900 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">Add Songs to Playlist</h2>
              <div className="space-y-4">
                {allSongs.map((song) => (
                  <div
                    key={song.id}
                    className={`p-4 rounded-lg cursor-pointer transition-colors ${
                      selectedSongs.has(song.id)
                        ? "bg-green-900"
                        : "bg-neutral-800 hover:bg-neutral-700"
                    }`}
                    onClick={() => handleSongSelect(song.id)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-semibold">{song.name}</h3>
                        <p className="text-neutral-400">{song.artist}</p>
                      </div>
                      {selectedSongs.has(song.id) && (
                        <svg
                          className="h-6 w-6 text-green-500"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 flex justify-end gap-4">
                <button
                  onClick={handleCloseAddSongsModal}
                  className="px-4 py-2 bg-neutral-700 hover:bg-neutral-600 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSelectedSongs}
                  disabled={selectedSongs.size === 0 || isAddingSongs}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAddingSongs ? (
                    <div className="flex items-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Adding...
                    </div>
                  ) : (
                    `Add ${selectedSongs.size} Songs`
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaylistPage;
