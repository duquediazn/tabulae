import { useState } from "react";
import ErrorMessage from "./ErrorMessage";
import { createCategory } from "../api/products";
import { useAuth } from "../context/useAuth";

export default function CreateInlineCategory({ onCategoryCreated }) {
  const { accessToken } = useAuth();
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleAdd = async () => {
    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    try {
      const newCategory = await createCategory(name.trim(), accessToken);
      onCategoryCreated(newCategory);
      setName("");
      setError("");
    } catch (e) {
      setError(e.message || "Failed to create category");
    }
  };

  return (
    <div className="mt-4 space-y-1">
      <label
        htmlFor="category"
        className="block text-sm font-medium text-gray-700"
      >
        Can't find the category?
      </label>
      <div className="flex gap-2">
        <input
          id="category"
          type="text"
          placeholder="New category"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="flex-1 border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          role="button"
          type="button"
          onClick={handleAdd}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-sm"
        >
          Add
        </button>
      </div>
      <ErrorMessage message={error} />
    </div>
  );
}
