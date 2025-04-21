import React, { useState } from 'react';

const RenamePlaylistModal = ({ isOpen, onClose, playlistName, onRename }) => {
  const [newName, setNewName] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newName.trim()) {
      setError('Please enter a new name');
      return;
    }
    try {
      await onRename(newName);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-neutral-800 p-6 rounded-lg w-full max-w-md">
        <h2 className="text-2xl font-bold text-white mb-4">Rename Playlist</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-white mb-2">Current Name</label>
            <input
              type="text"
              value={playlistName}
              disabled
              className="w-full p-2 bg-neutral-700 text-white rounded"
            />
          </div>
          <div className="mb-4">
            <label className="block text-white mb-2">New Name</label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full p-2 bg-neutral-700 text-white rounded"
              placeholder="Enter new playlist name"
            />
          </div>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-neutral-700 text-white rounded hover:bg-neutral-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Rename
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RenamePlaylistModal; 