import { useState } from "react";
import { useNavigate } from "react-router-dom";

const AlbumCard = ({ id, name, artist, image }) => {
  const [clicked, setClicked] = useState(false);
  const navigate = useNavigate();

  const handleClick = () => {
    if (clicked) {
      navigate(`/albums/${id}`);
    } else {
      setClicked(true);
      setTimeout(() => setClicked(false), 1000);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`w-full bg-neutral-900 hover:bg-neutral-800 transition duration-200 p-1 rounded-xl cursor-pointer shadow-md hover:shadow-lg group border ${
        clicked ? "border-green-400" : "border-transparent"
      }`}
    >
      {/* Album Cover */}
      <div className="relative w-full aspect-square overflow-hidden rounded-lg">
        <img
          src={image || "https://placehold.co/400x400?text=Album"}
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => (e.target.src = "https://placehold.co/400x400?text=Album")}
        />
      </div>

      {/* Album Info */}
      <div className="mt-4">
        <h3 className="text-white text-sm font-semibold truncate">{name}</h3>
        <p className="text-zinc-400 text-xs truncate">{artist}</p>
      </div>
    </div>
  );
};

export default AlbumCard;
