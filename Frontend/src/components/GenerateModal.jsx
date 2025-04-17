import React from "react";

const GenerateModal = ({ title, onConfirm, onCancel }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-neutral-900 p-6 rounded-xl shadow-lg max-w-sm w-full text-center">
        <h2 className="text-white text-lg font-bold mb-4">{title || "Are you sure?"}</h2>
        <div className="flex justify-center gap-4">
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Yes
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-zinc-600 text-white rounded hover:bg-zinc-700"
          >
            No
          </button>
        </div>
      </div>
    </div>
  );
};

export default GenerateModal;