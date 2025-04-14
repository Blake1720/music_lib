import React from 'react';

const SongCard = ({ image, title, artist }) => {
  return (
    <div className="w-full bg-neutral-900 hover:bg-neutral-800 transition duration-200 p-1 rounded-xl cursor-pointer shadow-md hover:shadow-lg group">
      {/* Album Art */}
      <div className="relative w-full aspect-square overflow-hidden rounded-lg">
        <img
          src={image || "https://placehold.co/400x400"}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => (e.target.src = "https://placehold.co/400x400")}
        />
      </div>

      {/* Song Info */}
      <div className="mt-4">
        <h3 className="text-white text-sm font-semibold truncate">{title}</h3>
        <p className="text-zinc-400 text-xs truncate">{artist}</p>
      </div>
    </div>
  );
};

export default SongCard;
