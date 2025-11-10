import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from "../context/useAuth";
import { getUserById, updateUser, deleteUser } from "../api/users";

export default function EditUser() {
  const { id } = useParams();
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "user",
    is_active: true,
    password: "",
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUserById(id, accessToken);
        setFormData({
          name: data.name,
          email: data.email,
          role: data.role,
          is_active: data.is_active,
          password: "",
        });
      } catch (error) {
        console.error("Error loading user:", error);
        alert("Could not load user");
        navigate("/users");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [id, accessToken, navigate]);

  useEffect(() => {
    document.title = "Edit User";
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await updateUser(id, accessToken, formData);
      alert("User updated successfully");
      navigate("/users");
    } catch (error) {
      alert("Error updating user:\n" + error.message);
    }
  };

  const handleDelete = async () => {
    const confirm = window.confirm(
      "Are you sure you want to delete this user?"
    );
    if (!confirm) return;

    try {
      await deleteUser(id, accessToken);
      alert("User deleted successfully");
      navigate("/users");
    } catch (error) {
      alert("Error deleting user:\n" + error.message);
    }
  };

  if (isLoading) {
    return (
      <>
        <Navbar />
        <Breadcrumb />
        <div className="p-6 text-gray-700">Loading user...</div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">Edit User</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Name
              </label>
              <input
                id="name"
                type="text"
                name="name"
                minLength={3}
                maxLength={100}
                value={formData.name}
                onChange={handleChange}
                className="h-[36px] bg-white w-full rounded border border-gray-300 px-3 py-1 text-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <ErrorMessage message={errors.name} />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                name="email"
                maxLength={100}
                value={formData.email}
                onChange={handleChange}
                className="h-[36px] bg-white w-full rounded border border-gray-300 px-3 py-1 text-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <ErrorMessage message={errors.email} />
            </div>

            {/* New password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                New Password
              </label>
              <input
                id="password"
                type="password"
                name="password"
                minLength={formData.password ? 8 : undefined}
                maxLength={255}
                value={formData.password}
                onChange={handleChange}
                className="h-[36px] bg-white w-full rounded border border-gray-300 px-3 py-1 text-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Leave blank to keep current"
              />
            </div>

            {/* Role */}
            <div>
              <label
                htmlFor="role"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Role
              </label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="h-[36px] bg-white w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            {/* Active */}
            <div htmlFor="is_active" className="flex items-center gap-2">
              <input
                id="is_active"
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
              <label htmlFor="is_active" className="text-sm text-gray-700">
                Active
              </label>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={() => navigate("/users")}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"
              >
                Cancel
              </button>
            </div>
          </form>

          <button
            onClick={handleDelete}
            className="mt-4 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded text-sm"
          >
            Delete User
          </button>
        </div>
      </div>
    </>
  );
}
