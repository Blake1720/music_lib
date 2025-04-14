import '../App.css';
import SongCard from '../components/SongCard';
import PlaylistCard from "../components/PlaylistCard";
import { useState } from 'react';

const Home = () => {
  const [songs, setSongs] = useState([
    { id: 1, title: 'Blinding Lights', artist: 'The Weeknd' },
    { id: 2, title: 'Save Your Tears', artist: 'The Weeknd' },
    { id: 3, title: 'Die for You', artist: 'The Weeknd' },
    { id: 4, title: 'After Hours', artist: 'The Weeknd' },
    { id: 5, title: 'Starboy', artist: 'The Weeknd' },
    { id: 6, title: 'In Your Eyes', artist: 'The Weeknd' },
    { id: 7, title: 'Can’t Feel My Face', artist: 'The Weeknd' },
    { id: 8, title: 'I Was Never There', artist: 'The Weeknd' },
  ]);
  const playlists = [
    {
      id: "1",
      name: "Chill Vibes",
      description: "Lo-fi and relaxing tunes",
      image: "https://placehold.co/100x100",
      url: "/playlists/1",
    },
    {
      id: "2",
      name: "Workout Hits",
      description: "High energy tracks to get you moving",
      image: "https://placehold.co/100x100",
      url: "/playlists/2",
    },
  ];

  return (
<div className="min-h-screen text-white px-4 py-10 flex justify-center bg-[linear-gradient(300deg,_#22c55e_30%,_#000_70%)]">
      <div className="w-full max-w-7xl">
        {/* Dashboard Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Your Music Dashboard
          </h1>
          <p className="text-zinc-400 mt-2 text-sm md:text-base">
            Dive into your collection of songs and playlists
          </p>
        </div>
        <div className="max-w-7xl mx-auto py-10 text-left">
        {/* Section Title */}
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
          Playlists
        </h2>
          {/* Playlist Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard key={playlist.id} {...playlist} />
          ))}
        </div>
      </div>

        {/* Song Grid */}
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-6 text-left">
          Recommended
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-8">
          {songs.map((song) => (
            <SongCard
              key={song.id}
              title={song.title}
              artist={song.artist}
              image="https://placehold.co/400x400"
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
