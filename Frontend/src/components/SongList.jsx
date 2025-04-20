import React from "react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const SongList = ({ id, image, title, artist, onCardClick }) => {
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
        className={`flex items-center gap-4 p-3 bg-neutral-900 hover:bg-neutral-800 transition rounded-lg shadow-sm group border 
        ${clicked ? "border-green-400" : "border-transparent"}`}>

        {/* Thumbnail */}
        <div className="w-12 h-12 flex-shrink-0 rounded-md overflow-hidden">
          <img
            src={image || "https://placehold.co/100x100"}
            alt={title}
            className="w-full h-full object-cover"
            onError={(e) => (e.target.src = "https://placehold.co/100x100")}
          />
        </div>

        {/* Info */}
        <div className="flex flex-col truncate">
          <span className="text-white text-sm font-medium truncate">{title}</span>
          <span className="text-zinc-400 text-xs truncate hover:text-green-400 hover:underline cursor-pointer"
          onClick={handleArtistClick}>{artist}</span>
        </div>
      </div>
  );
};

export default SongList;
