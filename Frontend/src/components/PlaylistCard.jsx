import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebase";

const PlaylistCard = ({ id, name, description, image, url, onRename }) => {
  const [clicked, setClicked] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [currentImage, setCurrentImage] = useState(image);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const username = auth.currentUser?.displayName;

  const handleClick = () => {
    if (clicked) {
      navigate(url);
    } else {
      setClicked(true);
      setTimeout(() => setClicked(false), 1000);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!username || isDeleting) return;

    setIsDeleting(true);
    try {
      const response = await fetch(
        `http://localhost:8000/database/playlists?username=${encodeURIComponent(username)}&playlist_name=${encodeURIComponent(name)}`,
        { method: "DELETE" }
      );
      
      if (!response.ok) throw new Error("Failed to delete playlist");
      
      window.location.reload();
    } catch (error) {
      console.error("Error deleting playlist:", error);
      alert("Failed to delete playlist. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleRename = (e) => {
    e.stopPropagation();
    if (onRename) {
      onRename({ id, name });
    }
  };

  const handleImageClick = (e) => {
    e.stopPropagation();
    e.preventDefault();
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleImageUpload = async (e) => {
    e.stopPropagation();
    const file = e.target.files?.[0];
    if (!file || !username) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('username', username);
      formData.append('playlist_name', name);

      const response = await fetch(
        'http://localhost:8000/database/playlists/image',
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Failed to upload image");

      const data = await response.json();
      setCurrentImage(data.image_url);
      
      // Refresh the page to update all instances of the playlist
      window.location.reload();
    } catch (error) {
      console.error("Error uploading image:", error);
      alert("Failed to upload image. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`w-full bg-neutral-900 hover:bg-neutral-800 cursor-pointer p-1 rounded-lg shadow-md border transition duration-200 flex flex-row gap-4 items-center justify-between ${
        clicked ? "border-green-400" : "border-transparent"
      }`}
    >
      <div className="flex flex-row gap-4 items-center">
        <div className="relative group">
          <img
            src={currentImage}
            alt={name}
            className="w-16 h-16 rounded-md object-cover"
            onError={(e) => (e.target.src = "https://placehold.co/64x64")}
            onClick={handleImageClick}
          />
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-md flex items-center justify-center cursor-pointer"
            onClick={handleImageClick}
          >
            {isUploading ? (
              <svg className="animate-spin h-6 w-6 text-white" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <span className="text-white text-sm">Change image</span>
            )}
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageUpload}
            accept="image/*"
            className="hidden"
          />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white truncate">{name}</h2>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={handleRename}
          className="p-2 text-neutral-400 hover:text-white transition-colors"
          title="Rename playlist"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="p-2 text-red-500 hover:text-red-400 transition-colors"
          title="Delete playlist"
        >
          {isDeleting ? (
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default PlaylistCard;
