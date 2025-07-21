import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import ErrorMessage from "../components/ErrorMessage";
import { createWarehouse } from "../api/warehouses";

export default function NewWarehouse() {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  const [description, setDescription] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!description.trim()) {
      newErrors.description = "Description is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);

    try {
      await createWarehouse({ description }, accessToken);
      alert("Warehouse successfully created");
      navigate("/warehouses/list");
    } catch (error) {
      alert(error.message || "Error creating warehouse");
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    document.title = "New Warehouse";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">New Warehouse</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Description
              </label>
              <input
                id="description"
                type="text"
                maxLength={255}
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full h-[36px] bg-white rounded border border-gray-300 px-3 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <ErrorMessage message={errors.description} />
            </div>

            <div className="flex gap-3">
              <button
                role="button"
                type="submit"
                disabled={isSubmitting}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded"
              >
                Save warehouse
              </button>
              <button
                role="button"
                type="button"
                onClick={() => navigate("/warehouses/list")}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
