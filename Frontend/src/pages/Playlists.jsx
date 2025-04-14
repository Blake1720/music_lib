import PlaylistCard from "../components/PlaylistCard";

const playlists = [
  {
    id: "1",
    name: "Chill Vibes",
    description: "Lo-fi and relaxing beats",
    image: "https://placehold.co/100x100",
    url: "/playlists/1",
  },
  {
    id: "2",
    name: "Workout Hits",
    description: "Pump-up tracks to keep you going",
    image: "https://placehold.co/100x100",
    url: "/playlists/2",
  },
  {
    id: "3",
    name: "Throwback Jams",
    description: "Hits from the 90s and 2000s",
    image: "https://placehold.co/100x100",
    url: "/playlists/3",
  },
  {
    id: "4",
    name: "Focus Mode",
    description: "Instrumental and ambient sounds",
    image: "https://placehold.co/100x100",
    url: "/playlists/4",
  },
];

const Playlists = () => {
  return (
    <div className="min-h-screen bg-neutral-950 text-white px-6 py-10">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-bold mb-8">Your Playlists</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard key={playlist.id} {...playlist} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Playlists;
