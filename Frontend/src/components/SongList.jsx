import React from "react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const SongItem = ({ id, title, artist, image, album_url, onCardClick }) => {
  const navigate = useNavigate();
  const [clicked, setClicked] = useState(false);

  const handleArtistClick = (e) => {
    e.stopPropagation();
    navigate(`/artists/${encodeURIComponent(artist)}`);
  };

  const handleClick = () => {
    if (clicked) {
      onCardClick?.({ id, title, artist });
    } else {
      setClicked(true);
      setTimeout(() => setClicked(false), 1000);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`flex items-center gap-4 p-3 bg-neutral-900 hover:bg-neutral-800 transition rounded-lg shadow-sm group border mb-2
      ${clicked ? "border-green-400" : "border-transparent"}`}
    >
      {/* Thumbnail */}
      <div className="w-12 h-12 flex-shrink-0 rounded-md overflow-hidden">
        <img
          src={album_url || image || "/album_cover.jpg"}
          alt={title}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.onerror = null; // Prevent infinite loop
            e.target.src = "/album_cover.jpg";
          }}
        />
      </div>

      {/* Info */}
      <div className="flex flex-col truncate w-full">
        <span className="text-white text-sm font-medium truncate text-left">{title}</span>
        <span
          className="text-zinc-400 text-xs truncate hover:text-green-400 hover:underline cursor-pointer text-left block"
          onClick={handleArtistClick}
        >
          {artist?.trim()}
        </span>
      </div>
    </div>
  );
};

const SongList = ({ songs, onCardClick }) => {
  if (!songs || songs.length === 0) {
    return <div className="text-zinc-500">No songs in this playlist.</div>;
  }

  return (
    <div className="space-y-2">
      {songs.map((song) => (
        <SongItem
          key={song.id}
          id={song.id}
          title={song.name}
          artist={song.artist?.trim()}
          image={song.image}
          album_url={song.album_url}
          onCardClick={onCardClick}
        />
      ))}
    </div>
  );
};

export default SongList;
