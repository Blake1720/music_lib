export const searchDatabase = (query) => {
    const lower = query.toLowerCase();
  
    return {
      artists: [
        { id: "a1", name: "The Weeknd", image: "https://placehold.co/100" },
        { id: "a2", name: "Dua Lipa", image: "https://placehold.co/100" },
      ].filter((a) => a.name.toLowerCase().includes(lower)),
  
      albums: [
        { id: "al1", name: "Tfter Hours", artist: "The Weeknd", image: "https://placehold.co/100" },
        { id: "al2", name: "Future Nostalgia", artist: "Dua Lipa", image: "https://placehold.co/100" },
      ].filter((al) => al.name.toLowerCase().includes(lower)),
  
      songs: [
        { id: "s1", title: "Tlinding Lights", artist: "The Weeknd" },
        { id: "s2", title: "Levitating", artist: "Dua Lipa" },
      ].filter((s) => s.title.toLowerCase().includes(lower)),
    };
  };
  