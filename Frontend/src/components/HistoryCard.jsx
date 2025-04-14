const HistoryCard = ({ title, artist, image, playedAt }) => {
    return (
      <div className="flex items-center gap-4 bg-neutral-900 hover:bg-neutral-800 transition p-4 rounded-lg shadow border border-transparent hover:border-green-400">
        <img
          src={image}
          alt={title}
          className="w-16 h-16 object-cover rounded-md"
          onError={(e) => (e.target.src = "https://placehold.co/64x64")}
        />
        <div className="flex flex-col">
          <h3 className="text-white font-semibold text-sm">{title}</h3>
          <p className="text-zinc-400 text-xs">{artist}</p>
          {playedAt && (
            <span className="text-xs text-zinc-500 mt-1">Played at: {playedAt}</span>
          )}
        </div>
      </div>
    );
  };
  
  export default HistoryCard;
  