import { useEffect, useState } from "react";
import { useAuth } from "../context/useAuth";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import Pagination from "../components/Pagination";
import { getAllWarehouses, warehousesBulkUpdate, deleteWarehouse } from "../api/warehouses";
import { useNavigate } from "react-router-dom";
import SearchInput from "../components/SearchInput";
import SelectFilter from "../components/SelectFilter";
import ContainerFilters from "../components/ContainerFilters";
import { showStatusSummary } from "../utils/showStatusSummary";
import ExportCSVButton from "../components/ExportCSVButton";
import { exportFilteredWarehousesCSV } from "../utils/export";
import API_URL from "../api/config";

export default function WarehouseList() {
  const { accessToken, user } = useAuth();
  const navigate = useNavigate();
  const [warehouses, setWarehouses] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isActive, setStatus] = useState("");
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState([]);

  const fetchWarehouses = async () => {
    setIsLoading(true);
    try {
      const response = await getAllWarehouses(
        accessToken,
        limit,
        offset,
        searchTerm,
        isActive
      );
      setWarehouses(response.data);
      setTotal(response.total);
    } catch (err) {
      console.error("Error loading warehouses:", err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWarehouses();
  }, [searchTerm, isActive, offset, limit, accessToken]);

  const toggleSelected = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this warehouse?");
    if (!confirmDelete) return;

    try {
      await deleteWarehouse(id, accessToken);
      alert("Warehouse deleted successfully");
      fetchWarehouses();
    } catch (error) {
      alert(error.message || "Error deleting the product");
    }
  };

  useEffect(() => {
    document.title = "Warehouses List";
  }, []);

  const toggleAll = () => {
    if (selected.length === warehouses.length) {
      setSelected([]);
    } else {
      setSelected(warehouses.map((w) => w.id));
    }
  };

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 mx-auto space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-800">Warehouses List</h1>
          {user?.role === "admin" && (
            <button
              role="button"
              onClick={() => navigate("/warehouses/new")}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm"
            >
              + New Warehouse
            </button>
          )}
        </div>

        <ContainerFilters
          extraContent={
            <ExportCSVButton
              onExport={() =>
                exportFilteredWarehousesCSV({
                  accessToken,
                  apiUrl: API_URL,
                  filters: {
                    searchTerm,
                    isActive,
                  },
                })
              }
              label="📤 Export CSV"
            />
          }
        >
          <SearchInput
            label="Search"
            placeholder="Search by description..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setOffset(0);
            }}
          />

          <SelectFilter
            label="Status"
            value={isActive}
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
        </ContainerFilters>

        {user?.role === "admin" && selected.length > 0 && (
          <div className="flex gap-2">
            <button
              role="button"
              onClick={async () => {
                try {
                  const res = await warehousesBulkUpdate(
                    selected.map((c) => parseInt(c)),
                    true,
                    accessToken
                  );
                  showStatusSummary(res, "warehouses", "activate");
                  setSelected([]);
                  await fetchWarehouses();
                } catch (error) {
                  alert(
                    error.message || "Error activating selected warehouses"
                  );
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
                  const res = await warehousesBulkUpdate(
                    selected.map((c) => parseInt(c)),
                    false,
                    accessToken
                  );
                  showStatusSummary(res, "warehouses", "deactivate");
                  setSelected([]);
                  await fetchWarehouses();
                } catch (error) {
                  alert(
                    error.message || "Error deactivating selected warehouses"
                  );
                }
              }}
              className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              Deactivate selected
            </button>
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-gray-500">Loading warehouses...</p>
        ) : (
          <div className="mt-4 overflow-x-auto bg-white shadow rounded">
            <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
              <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={
                        warehouses.length > 0 &&
                        selected.length === warehouses.length
                      }
                      onChange={toggleAll}
                    />
                  </th>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {warehouses.map((w) => (
                  <tr key={w.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">
                      <input
                        type="checkbox"
                        checked={selected.includes(w.id)}
                        onChange={() => toggleSelected(w.id)}
                      />
                    </td>
                    <td className="px-4 py-2">{w.id}</td>
                    <td className="px-4 py-2">{w.description}</td>
                    <td className="px-4 py-2">
                      {w.is_active ? (
                        <span className="text-green-600 font-medium">
                          Active
                        </span>
                      ) : (
                        <span className="text-red-500 font-medium">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 space-x-2">
                      <button
                        role="button"
                        onClick={() => navigate(`/warehouses/${w.id}`)}
                        className="text-indigo-600 hover:underline"
                      >
                        View
                      </button>
                      <button
                        role="button"
                        onClick={() => {
                          console.log(
                            "Navigating to stock of warehouse:",
                            w
                          );
                          navigate(`/stock/warehouse/${w.id}`);
                        }}
                        className="text-indigo-600 hover:underline"
                      >
                        View stock
                      </button>
                      {user?.role === "admin" && (
                        <>
                          <button
                            role="button"
                            onClick={() => navigate(`/warehouses/${w.id}/edit`)}
                            className="text-indigo-600 hover:underline"
                          >
                            Edit
                          </button>
                          <button
                            role="button"
                            onClick={() => handleDelete(w.id)}
                            className="text-red-600 hover:underline"
                          >
                            Delete
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
