import { useParams } from "react-router-dom";
import { playlists } from "../data/mockPlaylists";

const PlaylistPage = () => {
  const { playlistId } = useParams();
  const playlist = playlists[playlistId];

  if (!playlist) {
    return <div className="text-white p-10">Playlist not found.</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-6 mb-10">
          <img
            src={playlist.image}
            alt={playlist.name}
            className="w-32 h-32 object-cover rounded-lg"
          />
          <div>
            <h1 className="text-3xl font-bold">{playlist.name}</h1>
          </div>
        </div>

        {/* Song List */}
        <div className="space-y-4">
          {playlist.songs.map((song) => (
            <div
              key={song.id}
              className="bg-neutral-900 hover:bg-neutral-800 transition p-4 rounded-lg shadow-md"
            >
              <h2 className="text-sm font-semibold">{song.title}</h2>
              <p className="text-xs text-zinc-400">{song.artist}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PlaylistPage;
