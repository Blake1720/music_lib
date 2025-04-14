import { useState } from "react";
import { useNavigate } from "react-router-dom";

const PlaylistCard = ({ id, name, description, image, url }) => {
  const [clicked, setClicked] = useState(false);
  const navigate = useNavigate();

  const handleClick = () => {
    if (clicked) {
      navigate(url);
    } else {
      setClicked(true);
      setTimeout(() => setClicked(false), 1000);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`w-full bg-neutral-900 hover:bg-neutral-800 cursor-pointer p-1 rounded-lg shadow-md border transition duration-200 flex flex-row gap-4 items-center ${
        clicked ? "border-green-400" : "border-transparent"
      }`}
    >
      <img
        src={image}
        alt={name}
        className="w-16 h-16 rounded-md object-cover"
        onError={(e) => (e.target.src = "https://placehold.co/64x64")}
      />
      <div>
        <h2 className="text-sm font-semibold text-white truncate">{name}</h2>
      </div>
    </div>
  );
};

export default PlaylistCard;
