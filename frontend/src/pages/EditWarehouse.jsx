import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from "../context/useAuth";
import { getWarehouseById, warehouseUpdate } from "../api/warehouses";

export default function EditWarehouse() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { accessToken, user } = useAuth();

  const [form, setForm] = useState({
    description: "",
    is_active: true,
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchWarehouse = async () => {
      try {
        const warehouse = await getWarehouseById(id, accessToken);
        setForm({
          description: warehouse.description,
          is_active: warehouse.is_active,
        });
      } catch (error) {
        console.error("Error loading warehouse:", error);
        alert("Failed to load warehouse");
        navigate("/warehouses/list");
      } finally {
        setIsLoading(false);
      }
    };

    fetchWarehouse();
  }, [id, accessToken, navigate]);

  useEffect(() => {
    document.title = "Edit Warehouse";
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const validate = () => {
    const newErrors = {};
    if (!form.description.trim()) {
      newErrors.description = "Description is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await warehouseUpdate(id, form, accessToken);
      alert("Warehouse updated successfully");
      navigate(`/warehouses/${id}`);
    } catch (error) {
      console.error("Error updating warehouse:", error);
      alert(error.message || "Failed to update warehouse");
    }
  };

  if (isLoading) {
    return (
      <>
        <Navbar />
        <Breadcrumb />
        <div className="p-6 text-gray-700">Loading warehouse...</div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">Edit warehouse</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Description */}
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
                name="description"
                value={form.description}
                maxLength={255}
                required
                onChange={handleChange}
                className="h-[36px] bg-white w-full rounded border border-gray-300 px-3 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <ErrorMessage message={errors.description} />
            </div>

            {/* Active (admin only) */}
            {user?.role === "admin" && (
              <div className="flex items-center gap-2">
                <input
                  id="is_active"
                  type="checkbox"
                  name="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                />
                <label htmlFor="is_active" className="text-sm text-gray-700">
                  Active
                </label>
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded"
              >
                Save changes
              </button>
              <button
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
