import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import NavBar from "./components/NavBar";
import SideBar from "./components/SideBar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import SearchResults from "./pages/SearchResults";
import AlbumPage from "./pages/AlbumPage"
import ArtistPage from "./pages/ArtistPage"
import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";
import Playlists from "./pages/Playlists";
import PlaylistPage from "./pages/PlaylistPage";

function App() {
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setAuthChecked(true);
      console.log("User changed:", currentUser);
    });
    return () => unsubscribe();
  }, []);

  if (!authChecked) {
    return <div className="text-white p-10">Loading...</div>;
  }
  
  return (
    <Router>
      <div className="flex">
        {/* Sidebar */}
        {user && <SideBar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />}

        {/* Main Content */}
        <div
          className={`flex-1 min-h-screen transition-all duration-300 ${
            user ? (isSidebarOpen ? "ml-64" : "ml-20") : ""
          }`}
        >
          {user && <NavBar />}
            {user ? (
              <>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/playlists" element={<Playlists />} />
                <Route path="/playlists/:playlistName" element={<PlaylistPage />} />
                <Route path="/albums/:albumId" element={<AlbumPage />} />
                <Route path="/artists/:artistName" element={<ArtistPage />} />
                <Route path="/search" element={<SearchResults />} />
              </Routes>
              </>
            ) : (
              <>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<Navigate to="/login" />} />
              </Routes>
              </>
            )}
        </div>
      </div>
    </Router>
  );
}

export default App;
