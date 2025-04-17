import React from "react";
import { Home, Music, LogOut} from "lucide-react";
import { Link } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../firebase"; // or your config path

const handleLogout = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("Logout error:", error);
  }
};
const SideBar = ({ isOpen, setIsOpen }) => {
  const navItems = [
    { icon: <Home size={20} />, label: "Home", path: "/" },
    { icon: <Music size={20} />, label: "Playlists", path: "/playlists" },
  ];

  return (
    <div
      className={`bg-neutral-900 fixed top-0 left-0 z-20 h-full transition-all duration-300 ${
        isOpen ? "w-64" : "w-20"
      } shadow-md flex flex-col`}
    >
      {/* Header + Toggle Button */}
      <div className="flex justify-between items-center px-4 py-5 border-b border-neutral-800">
        <span className="text-xl font-bold text-green-400">
          {isOpen ? (
            <div className="text-2xl font-bold tracking-tight">
              <span className="text-white">Music</span>
              <span className="text-green-400">Lib</span>
            </div>
          ) : (
            ""
          )}
        </span>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-zinc-400 hover:text-white"
        >
          {isOpen ? "<" : ">"}
        </button>
      </div>

      {/* Navigation Items */}
      <ul className="flex flex-col space-y-4 px-4 mt-6">
      {navItems.map((item, index) => (
        <li key={index}>
          <Link
            to={item.path}
            className={`flex items-center gap-3 p-2 rounded-md hover:text-green-400 transition text-zinc-400 ${
              isOpen ? "justify-start" : "justify-center"
            }`}
          >
            <div
              className={`transition-transform ${
                isOpen ? "text-base" : "text-2xl"
              }`}
            >
              {item.icon}
            </div>
            {isOpen && <span className="text-sm">{item.label}</span>}
          </Link>
        </li>
      ))}

<li>
  <div
    onClick={handleLogout}
    className={`flex items-center gap-3 p-2 rounded-md hover:text-green-400 transition ${
      isOpen ? "justify-start" : "justify-center"
    }`}
  >
    <LogOut size={20} />
    {isOpen && <span className="text-sm">Logout</span>}
  </div>
</li>
      </ul>
    </div>
  );
};

export default SideBar;
