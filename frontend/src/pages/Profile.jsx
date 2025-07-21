import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";
import { updateUser } from "../api/users";
import { verifyPassword } from "../api/auth";

export default function Profile() {
  const { user, accessToken, setUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [role, setRole] = useState(user?.role || "");
  const [editMode, setEditMode] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setEmail(user.email || "");
      setRole(user.role || "");
    }
  }, [user]);

  useEffect(() => {
    document.title = "Profile";
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await verifyPassword(password, accessToken);
    } catch {
      setErrorMsg("Incorrect password. No changes were made.");
      return;
    }

    try {
      await updateUser(user.id, accessToken, { name, email });
      setEditMode(false);
      setSuccessMsg("Profile updated successfully.");
      setUser((prev) => ({ ...prev, name, email }));
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  return (
    <>
      <Navbar />
      <div className="flex justify-center pt-12 h-screen">
        <div className="space-y-12 w-full max-w-2xl px-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            Your profile
          </h2>
          <p className="text-sm text-gray-600">
            Here you can view and update your account details.
          </p>

          <form onSubmit={handleUpdate} className="space-y-3">
            {/* Name */}
            <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label
                  htmlFor="name"
                  className="block text-sm/6 font-medium text-gray-900"
                >
                  Name
                </label>
                <div className="mt-2">
                  <div className="flex items-center rounded-md pl-3 outline-1 -outline-offset-1 outline-gray-300 focus-within:outline-2 focus-within:-outline-offset-2 focus-within:outline-indigo-600">
                    <input
                      id="name"
                      name="name"
                      type="text"
                      minLength={3}
                      maxLength={100}
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      readOnly={!editMode}
                      className={`block min-w-0 grow py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6 ${
                        editMode ? "bg-white" : "bg-gray-100"
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Email */}
            <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label
                  htmlFor="email"
                  className="block text-sm/6 font-medium text-gray-900"
                >
                  Email
                </label>
                <div className="mt-2">
                  <div className="flex items-center rounded-md pl-3 outline-1 -outline-offset-1 outline-gray-300 focus-within:outline-2 focus-within:-outline-offset-2 focus-within:outline-indigo-600">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={email}
                      maxLength={100}
                      onChange={(e) => setEmail(e.target.value)}
                      readOnly={!editMode}
                      className={`block min-w-0 grow py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6 ${
                        editMode ? "bg-white" : "bg-gray-100"
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Password verification */}
            {editMode && (
              <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                <div className="sm:col-span-4">
                  <label
                    htmlFor="password"
                    className="block text-sm/6 font-medium text-gray-900"
                  >
                    Password (required to confirm changes)
                  </label>
                  <div className="mt-2">
                    <div className="flex items-center rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 focus-within:outline-2 focus-within:-outline-offset-2 focus-within:outline-indigo-600">
                      <input
                        id="password"
                        name="password"
                        type="password"
                        minLength={8}
                        maxLength={255}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="block min-w-0 grow py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6"
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Role */}
            <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label className="block text-sm/6 font-medium text-gray-900">
                  Role
                </label>
                <div className="mt-2">
                  <p>{role}</p>
                </div>
              </div>
            </div>
          </form>

          {/* Messages */}
          {errorMsg && <p className="text-red-500 text-sm">{errorMsg}</p>}
          {successMsg && <p className="text-green-600 text-sm">{successMsg}</p>}

          {/* Buttons */}
          <div className="flex gap-4 mt-6">
            {editMode ? (
              <>
                <button
                  role="button"
                  type="submit"
                  onClick={handleUpdate}
                  className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
                >
                  Save changes
                </button>
                <button
                  role="button"
                  type="button"
                  onClick={() => {
                    setPassword("");
                    setEditMode(false);
                    setErrorMsg("");
                    setSuccessMsg("");
                    setName(user.name || "");
                    setEmail(user.email || "");
                  }}
                  className="inline-flex items-center rounded-md bg-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-400"
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                role="button"
                type="button"
                onClick={() => setEditMode(true)}
                className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
              >
                Edit
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
