import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import Pagination from "../components/Pagination";
import SearchInput from "../components/SearchInput";
import SelectFilter from "../components/SelectFilter";
import FiltersContainer from "../components/ContainerFilters";
import ExportCSVButton from "../components/ExportCSVButton";
import { useAuth } from "../context/useAuth";
import { useNavigate } from "react-router-dom";
import {
  getUsers,
  deleteUser,
  usersBulkStatus,
} from "../api/users";
import UsersListTable from "../components/UsersListTable";
import { exportFilteredUsersCSV } from "../utils/export";
import API_URL from "../api/config";

export default function Users() {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [is_active, setStatus] = useState("");
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const { data, total } = await getUsers({
        accessToken,
        limit,
        offset,
        searchTerm,
        is_active,
      });
      setUsers(data || []);
      setTotal(total || 0);
    } catch (error) {
      console.error("Error loading users:", error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [searchTerm, is_active, offset, limit]);

  useEffect(() => {
    document.title = "Users";
  }, []);

  const handleDelete = async (id) => {
    const confirm = window.confirm("Delete this user?");
    if (!confirm) return;

    try {
      await deleteUser(id, accessToken);
      alert("User deleted");
      fetchUsers();
    } catch (error) {
      alert(error.message);
    }
  };

  const toggleSelected = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const toggleAll = () => {
    if (selected.length === users.length) {
      setSelected([]);
    } else {
      setSelected(users.map((u) => u.id));
    }
  };

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 mx-auto space-y-6 max-w-7xl">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <h1 className="text-2xl font-bold text-gray-800">Users</h1>
          <button
            role="button"
            onClick={() => navigate("/users/new")}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm"
          >
            + Create user
          </button>
        </div>

        <FiltersContainer
          extraContent={
            <ExportCSVButton
              onExport={() =>
                exportFilteredUsersCSV({
                  accessToken,
                  filters: { is_active, searchTerm },
                  apiUrl: API_URL,
                })
              }
              label="📤 Export CSV"
            />
          }
        >
          <SearchInput
            label="Search"
            placeholder="Search by name or email..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setOffset(0);
            }}
          />
          <SelectFilter
            label="Status"
            value={is_active}
            onChange={(e) => {
              setStatus(e.target.value);
              setOffset(0);
            }}
            options={[
              { value: "", label: "All" },
              { value: "true", label: "Active" },
              { value: "false", label: "Inactive" },
            ]}
          />
        </FiltersContainer>

        {selected.length > 0 && (
          <div className="flex gap-2">
            <button
              role="button"
              onClick={async () => {
                try {
                  await usersBulkStatus(selected, true, accessToken);
                  alert("Users activated");
                  setSelected([]);
                  fetchUsers();
                } catch (e) {
                  alert(e.message);
                }
              }}
              className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm"
            >
              Activate selected
            </button>
            <button
              role="button"
              onClick={async () => {
                try {
                  await usersBulkStatus(selected, false, accessToken);
                  alert("Users deactivated");
                  setSelected([]);
                  fetchUsers();
                } catch (e) {
                  alert(e.message);
                }
              }}
              className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              Deactivate selected
            </button>
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-gray-500">Loading users...</p>
        ) : (
          <UsersListTable
            users={users}
            onDelete={handleDelete}
            selected={selected}
            toggleSelected={toggleSelected}
            toggleAll={toggleAll}
          />
        )}

        <Pagination
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={(newOffset) => setOffset(newOffset)}
        />
      </div>
    </>
  );
}
