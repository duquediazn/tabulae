import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import {
  getProductStockByWarehouse,
  getProductHistoryByWarehouse,
} from "../api/stock";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";
import Pagination from "../components/Pagination";

export default function ProductStockByWarehouse() {
  const { warehouse_id, product_id } = useParams();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const [stock, setStock] = useState([]);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [warehouseName, setWarehouseName] = useState("");
  const [productName, setProductName] = useState("");
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    document.title = "Product Stock by Warehouse";
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getProductStockByWarehouse(
          warehouse_id,
          product_id,
          accessToken,
          limit,
          offset
        );
        setStock(data.data);
        setTotal(data.total);

        if (data.data.length > 0) {
          setWarehouseName(data.data[0].warehouse_name);
          setProductName(data.data[0].product_name);
        }

        const historyData = await getProductHistoryByWarehouse(
          warehouse_id,
          product_id,
          accessToken
        );

        const sorted = [...historyData.data].sort(
          (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );

        let accumulatedStock = 0;
        const chartData = sorted.map((entry) => {
          const moveType = entry.move_type?.toLowerCase().trim();
          const change = moveType === "incoming" ? entry.quantity : -entry.quantity;
          accumulatedStock += change;
          return {
            created_at: entry.created_at?.split("T")[0] ?? "No date",
            quantity: accumulatedStock,
          };
        });

        setHistory(chartData);

      } catch (error) {
        console.error("Error fetching product stock:", error);
        alert("Could not load product stock for this warehouse.");
        navigate("/warehouses");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [warehouse_id, product_id, accessToken, navigate, limit, offset]);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">
            Stock of {productName} in {warehouseName} (#{warehouse_id})
          </h1>

          <button
            role="button"
            onClick={() => navigate(-1)}
            className="text-indigo-600 hover:underline text-sm"
          >
            ← Go back
          </button>

          {/* History chart */}
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Stock history
          </h2>
          <div className="bg-white rounded shadow p-4">
            {history.length === 0 ? (
              <p className="text-sm text-gray-500">
                No recorded movements for this product.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <div className="min-w-[600px]">
                  <LineChart width={600} height={300} data={history}>
                    <XAxis dataKey="created_at" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="quantity" stroke="#10b981" />
                  </LineChart>
                </div>
              </div>
            )}
          </div>

          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Current stock
          </h2>
          {isLoading ? (
            <p className="text-sm text-gray-600">Loading...</p>
          ) : stock.length === 0 ? (
            <p className="text-sm text-gray-600">
              No stock registered for this product in this warehouse.
            </p>
          ) : (
            <div className="overflow-x-auto bg-white shadow rounded">
              <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
                <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase">
                  <tr>
                    <th className="px-4 py-3">SKU</th>
                    <th className="px-4 py-3">Lot</th>
                    <th className="px-4 py-3">Expiration date</th>
                    <th className="px-4 py-3">Quantity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {stock.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-2">{item.sku}</td>
                      <td className="px-4 py-2">{item.lot}</td>
                      <td className="px-4 py-2">
                        {item.expiring ? item.expiring.split("T")[0] : "-"}
                      </td>
                      <td className="px-4 py-2">{item.quantity}</td>
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
      </div>
    </>
  );
}
