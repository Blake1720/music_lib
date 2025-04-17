import { useState } from "react";
import { useNavigate } from "react-router-dom";

const ArtistCard = ({ id, image, name }) => {
    const [clicked, setClicked] = useState(false);
    const navigate = useNavigate();
  
    const handleClick = () => {
      if (clicked) {
        navigate(`/artists/${name}`);
      } else {
        setClicked(true);
        setTimeout(() => setClicked(false), 1000);
      }
    };
  return (
    <div
    onClick={handleClick}
    className={`w-full bg-neutral-900 hover:bg-neutral-800 transition duration-200 p-1 rounded-xl cursor-pointer shadow-md hover:shadow-lg group"${
      clicked ? "border-green-400" : "border-transparent"
    }`}>
      {/* Artist Image */}
      <div className="relative w-full aspect-square overflow-hidden rounded-lg">
        <img
          src={image || "https://placehold.co/400x400?text=Artist"}
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => (e.target.src = "https://placehold.co/400x400?text=Artist")}
        />
      </div>

      {/* Name */}
      <div className="mt-4">
        <h3 className="text-white text-sm font-semibold truncate">{name}</h3>
        <p className="text-zinc-400 text-xs truncate">Artist</p>
      </div>
    </div>
  );
};

export default ArtistCard;
