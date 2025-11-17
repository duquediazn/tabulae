import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../context/useAuth";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { getProductHistoryByWarehouse } from "../api/stock";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";
import Pagination from "../components/Pagination";

export default function ProductHistoryByWarehouse() {
  const { warehouse_id, product_id } = useParams();
  const { accessToken } = useAuth();
  const [chartData, setChartData] = useState([]);
  const [historyTable, setHistoryTable] = useState([]);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [sku, setSku] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchChart = async () => {
      try {
        const data = await getProductHistoryByWarehouse(
          warehouse_id,
          product_id,
          accessToken,
          100
        );

        if (data.data.length > 0) {
          setSku(data.data[0].sku);
        }

        const sorted = [...data.data].sort(
          (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );

        let stock = 0;
        const cumulative = sorted.map((mov) => {
          const moveType = mov.move_type?.toLowerCase().trim();
          const change = moveType === "incoming" ? mov.quantity : -mov.quantity;
          stock += change;
          return {
            created_at: mov.created_at?.split("T")[0] ?? "No date",
            quantity: stock,
          };
        });

        setChartData(cumulative);
      } catch (error) {
        console.error("Error fetching chart data:", error.message);
      }
    };

    fetchChart();
  }, [warehouse_id, product_id, accessToken]);

  useEffect(() => {
    const fetchTable = async () => {
      try {
        setIsLoading(true);
        const data = await getProductHistoryByWarehouse(
          warehouse_id,
          product_id,
          accessToken,
          limit,
          offset
        );
        setHistoryTable(data.data);
        setTotal(data.total);
      } catch (error) {
        console.error("Error fetching movement history:", error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTable();
  }, [warehouse_id, product_id, accessToken, limit, offset]);

  useEffect(() => {
    document.title = "Product History by Warehouse";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          {`History of product ${sku} in warehouse ${warehouse_id}`}
        </h1>
        <button
          role="button"
          onClick={() => window.history.back()}
          className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Go back
        </button>

        {/* Chart */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-bold text-gray-700 mb-4">
            Stock evolution
          </h2>
          {chartData.length > 0 ? (
            <div className="overflow-x-auto">
              <div className="min-w-[600px]">
                <LineChart width={600} height={250} data={chartData}>
                  <XAxis dataKey="created_at" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="quantity"
                    stroke="#3b82f6"
                    strokeWidth={2}
                  />
                </LineChart>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No data available.</p>
          )}
        </div>

        {/* Table */}
        <h2 className="text-lg font-bold text-gray-700">
          Movement history
        </h2>

        <div className="bg-white shadow rounded overflow-x-auto">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading history...</p>
          ) : historyTable.length === 0 ? (
            <p className="text-sm text-gray-500">
              No movements recorded.
            </p>
          ) : (
            <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
              <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-2">Movement ID</th>
                  <th className="px-4 py-2">Date</th>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">SKU</th>
                  <th className="px-4 py-2">Lot</th>
                  <th className="px-4 py-2">Quantity</th>
                  <th className="px-4 py-2">Warehouse</th>
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
                    <td className="px-4 py-2">{h.warehouse_id}</td>
                    <td className="px-4 py-2">{h.user_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
    </>
  );
}
