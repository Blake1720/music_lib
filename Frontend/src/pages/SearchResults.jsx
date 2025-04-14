import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { searchDatabase } from "../data/mockSearchResults";

const SearchResults = () => {
  const { search } = useLocation(); // ?q=...
  const query = new URLSearchParams(search).get("q") || "";
  const [results, setResults] = useState({ artists: [], albums: [], songs: [] });

  useEffect(() => {
    if (query.trim() !== "") {
      const res = searchDatabase(query);
      setResults(res);
    }
  }, [query]);

  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Search results for: <span className="text-green-400">{query}</span></h1>

      {results.artists.length > 0 && (
        <>
          <h2 className="text-xl font-semibold mb-8">Artists</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-10">
            {results.artists.map((a) => (
              <div key={a.id} className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg text-center">
                <img src={a.image} alt={a.name} className="w-24 h-24 mx-auto rounded-full mb-2 object-cover" />
                <p className="text-sm font-medium">{a.name}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {results.albums.length > 0 && (
        <>
          <h2 className="text-xl font-semibold mb-8">Albums</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-10">
            {results.albums.map((al) => (
              <div key={al.id} className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg text-center">
                <img src={al.image} alt={al.name} className="w-24 h-24 mx-auto rounded-md mb-2 object-cover" />
                <p className="text-sm font-medium">{al.name}</p>
                <p className="text-xs text-zinc-400">{al.artist}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {results.songs.length > 0 && (
        <>
          <h2 className="text-xl font-semibold mb-8">Songs</h2>
          <div className="space-y-3">
            {results.songs.map((song) => (
              <div key={song.id} className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg">
                <p className="text-sm font-semibold">{song.title}</p>
                <p className="text-xs text-zinc-400">{song.artist}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {results.artists.length === 0 && results.albums.length === 0 && results.songs.length === 0 && (
        <p className="text-zinc-400 mt-10">No results found.</p>
      )}
    </div>
  );
};

export default SearchResults;
