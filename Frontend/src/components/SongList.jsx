import React from "react";

const SongList = ({ songs }) => {
  if (!songs || songs.length === 0) {
    return <p className="text-zinc-500">No songs found.</p>;
  }

  return (
    <div className="w-full space-y-2">
      {songs.map((song, index) => (
        <div
          key={song.id}
          className="flex items-center gap-4 p-3 bg-neutral-900 hover:bg-neutral-800 transition rounded-lg shadow-sm"
        >
          <div className="text-zinc-400 w-6 text-sm">{index + 1}</div>

          {/* Thumbnail */}
          <div className="w-12 h-12 flex-shrink-0 rounded-md overflow-hidden">
            <img
              src={song.image || "https://placehold.co/100x100"}
              alt={song.name}
              className="w-full h-full object-cover"
              onError={(e) => (e.target.src = "https://placehold.co/100x100")}
            />
          </div>

          {/* Info */}
          <div className="flex flex-col truncate">
            <span className="text-white text-sm font-medium truncate">{song.name}</span>
            <span className="text-zinc-400 text-xs truncate">{song.artist}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SongList;
