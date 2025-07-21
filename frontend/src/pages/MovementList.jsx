import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useState, useEffect } from "react";
import { useAuth } from "../context/useAuth";
import API_URL from "../api/config";
import Pagination from "../components/Pagination";
import { useNavigate } from "react-router-dom";
import { getStockMovements } from "../api/stock_moves";
import { getUsers } from "../api/users";
import ExportCSVButton from "../components/ExportCSVButton";
import { exportFilteredMovementsCSV } from "../utils/export";
import SearchInput from "../components/SearchInput";
import SelectFilter from "../components/SelectFilter";
import FilterContainer from "../components/ContainerFilters";

export default function MovementList() {
  const { accessToken, user } = useAuth();
  const navigate = useNavigate();
  const [movements, setMovements] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setfilterType] = useState("");
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [users, setUsers] = useState([]);
  const [userId, setuserId] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const { movements, total } = await getStockMovements({
          accessToken,
          filters: {
            searchTerm,
            filterType,
            dateFrom,
            dateTo,
            userId,
          },
          limit,
          offset,
        });
        setMovements(movements);
        setTotal(total);
      } catch (error) {
        console.error("Error loading movements:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [
    searchTerm,
    filterType,
    dateFrom,
    dateTo,
    userId,
    offset,
    limit,
    accessToken,
  ]);

  useEffect(() => {
    if (!isLoading && user?.role === "admin" && accessToken) {
      getUsers({ accessToken, limit: 50 })
        .then((res) => setUsers(res.data || []))
        .catch((err) => {
          console.error("Error loading users:", err.message);
        });
    }
  }, [accessToken, user, isLoading]);

  useEffect(() => {
    document.title = "Stock Movements List";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          Stock Movements List
        </h1>

        <FilterContainer
          extraContent={
            <ExportCSVButton
              onExport={() =>
                exportFilteredMovementsCSV({
                  accessToken,
                  apiUrl: API_URL,
                  filters: {
                    searchTerm,
                    filterType,
                    dateFrom,
                    dateTo,
                    userId,
                  },
                })
              }
              label="📤 Export CSV"
            />
          }
        >
          <div>
            <label
              htmlFor="date-from"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              From date
            </label>
            <input
              id="date-from"
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                setOffset(0);
              }}
              className="h-[36px] bg-white rounded border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label
              htmlFor="date-to"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              To date
            </label>
            <input
              id="date-to"
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                setOffset(0);
              }}
              className="h-[36px] bg-white rounded border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {user?.role === "admin" && (
            <SelectFilter
              label="User"
              value={userId}
              onChange={(e) => {
                setuserId(e.target.value);
                setOffset(0);
              }}
              options={[
                { value: "", label: "All" },
                ...users.map((u) => ({ value: u.id, label: u.name })),
              ]}
              className="max-w-[180px]"
            />
          )}

          <SelectFilter
            label="Type"
            value={filterType}
            onChange={(e) => {
              setfilterType(e.target.value);
              setOffset(0);
            }}
            options={[
              { value: "", label: "All" },
              { value: "incoming", label: "Incoming" },
              { value: "outgoing", label: "Outgoing" },
            ]}
            className="max-w-[150px]"
          />

          <SearchInput
            label="Search"
            placeholder="Search by user..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </FilterContainer>

        <div className="overflow-auto bg-white shadow rounded">
          <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">User</th>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Lines</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-4 text-center text-gray-500"
                  >
                    Loading movements...
                  </td>
                </tr>
              ) : movements.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-4 text-center text-gray-500"
                  >
                    No movements found.
                  </td>
                </tr>
              ) : (
                movements.map((mov) => (
                  <tr key={mov.move_id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{mov.move_id}</td>
                    <td className="px-4 py-2 capitalize">{mov.move_type}</td>
                    <td className="px-4 py-2">{mov.user_name}</td>
                    <td className="px-4 py-2">
                      {new Date(mov.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-2">{mov.lines?.length || 0}</td>
                    <td className="px-4 py-2">
                      <button
                        role="button"
                        onClick={() => navigate(`/stock-movements/${mov.move_id}`)}
                        className="text-indigo-600 hover:underline text-sm"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

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
