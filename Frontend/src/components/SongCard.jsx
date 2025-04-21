import React from "react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const SongCard = ({ id, image, title, artist, onCardClick, album_url }) => {
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
    className={`w-full bg-neutral-900 hover:bg-neutral-800 transition duration-200 p-1 rounded-xl cursor-pointer shadow-md hover:shadow-lg group border ${clicked ? "border-green-400" : "border-transparent"}`}


      >
      {/* Album Art */}
      <div className="relative w-full aspect-square overflow-hidden rounded-lg">
        <img
          src={album_url || image || "/album_cover.jpg"}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            e.target.onerror = null; // Prevent infinite loop
            e.target.src = "/album_cover.jpg";
          }}
        />
      </div>

      {/* Song Info */}
      <div className="mt-4">
        <h3
          className="text-white text-sm font-semibold truncate cursor-pointer"
        >
          {title}
        </h3>
        <p
          className="text-zinc-400 text-xs truncate hover:text-green-400 hover:underline cursor-pointer"
          onClick={handleArtistClick}
        >
          {artist}
        </p>
      </div>
    </div>
  );
};

export default SongCard;
