import HistoryCard from "../components/HistoryCard";

const historyItems = [
  {
    id: 1,
    title: "Blinding Lights",
    artist: "The Weeknd",
    image: "https://placehold.co/400x400",
    playedAt: "2024-04-13 10:32 PM",
  },
  {
    id: 2,
    title: "Levitating",
    artist: "Dua Lipa",
    image: "https://placehold.co/400x400",
    playedAt: "2024-04-13 10:15 PM",
  },
  // Add more...
];

const History = () => {
  return (
    <div className="min-h-screen bg-neutral-950 text-white px-4 py-10">
    <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Listening History</h1>

        <div className="space-y-4">
        {historyItems.map((item) => (
            <HistoryCard key={item.id} {...item} />
        ))}
        </div>
    </div>
    </div>
  );
};

export default History;
