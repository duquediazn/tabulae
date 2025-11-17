import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import { getWarehouseHistory } from "../api/stock";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";
import Pagination from "../components/Pagination";

export default function WarehouseStockHistory() {
  const { warehouse_id } = useParams();
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  const [warehouseName, setWarehouseName] = useState("");
  const [stockChart, setStockChart] = useState([]);
  const [historyTable, setHistoryTable] = useState([]);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Load chart data (once)
  useEffect(() => {
    const fetchChart = async () => {
      try {
        const result = await getWarehouseHistory(
          warehouse_id,
          accessToken,
          100
        );
        const data = result.data;

        if (data.length > 0) {
          setWarehouseName(data[0].warehouse_name || "");
        }

        const sorted = [...data].sort(
          (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );

        let stock = 0;
        const cumulative = sorted.map((mov) => {
          const delta = mov.move_type === "incoming" ? mov.quantity : -mov.quantity;
          stock += delta;
          return {
            created_at: mov.created_at.split("T")[0],
            quantity: stock,
          };
        });

        setStockChart(cumulative);
      } catch (error) {
        console.error("Error loading chart:", error);
      }
    };

    fetchChart();
  }, [warehouse_id, accessToken]);

  // Load table data (with pagination)
  useEffect(() => {
    const fetchTable = async () => {
      try {
        setIsLoading(true);
        const result = await getWarehouseHistory(
          warehouse_id,
          accessToken,
          limit,
          offset
        );
        setHistoryTable(result.data);
        setTotal(result.total);
      } catch (error) {
        console.error("Error loading history:", error);
        alert("Could not load warehouse history.");
        navigate("/warehouses");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTable();
  }, [warehouse_id, accessToken, limit, offset, navigate]);

  useEffect(() => {
    document.title = "Warehouse Stock History";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">
            Stock history at {warehouseName} (#{warehouse_id})
          </h1>

          <button
            role="button"
            onClick={() => navigate(-1)}
            className="text-indigo-600 hover:underline text-sm"
          >
            ← Back
          </button>

          {/* Chart */}
          <div className="bg-white rounded shadow p-4">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              Stock evolution
            </h2>
            {stockChart.length > 0 ? (
              <div className="overflow-x-auto">
                <div className="min-w-[600px]">
                  <LineChart width={600} height={300} data={stockChart}>
                    <XAxis dataKey="created_at" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="quantity" stroke="#3b82f6" />
                  </LineChart>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                Not enough data to display the chart.
              </p>
            )}
          </div>

          {/* Table */}
          <h2 className="text-lg font-semibold text-gray-700">
            Stock movement history
          </h2>

          <div className="bg-white shadow rounded overflow-x-auto">
            {isLoading ? (
              <p className="text-sm text-gray-500">Loading history...</p>
            ) : historyTable.length === 0 ? (
              <p className="text-sm text-gray-500">
                No movements found.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
                  <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <tr>
                      <th className="px-4 py-2">Movement ID</th>
                      <th className="px-4 py-2">Date</th>
                      <th className="px-4 py-2">Type</th>
                      <th className="px-4 py-2">SKU</th>
                      <th className="px-4 py-2">Lot</th>
                      <th className="px-4 py-2">Quantity</th>
                      <th className="px-4 py-2">Product</th>
                      <th className="px-4 py-2">User</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {historyTable.map((h, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-2">{h.move_id}</td>
                        <td className="px-4 py-2">
                          {new Date(h.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-2 capitalize">{h.move_type}</td>
                        <td className="px-4 py-2">{h.sku}</td>
                        <td className="px-4 py-2">{h.lot}</td>
                        <td className="px-4 py-2">{h.quantity}</td>
                        <td className="px-4 py-2">{h.product_id}</td>
                        <td className="px-4 py-2">{h.user_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          <Pagination
            total={total}
            limit={limit}
            offset={offset}
            onPageChange={(newOffset) => setOffset(newOffset)}
          />
        </div>
      </div>
    </>
  );
}
