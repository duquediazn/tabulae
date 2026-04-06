import Breadcrumb from "../components/Breadcrumb";
import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";
import { useAuth } from "../context/useAuth";
import {
  getSemaphore,
  getWarehouseDetail,
  getProductsByWarehousePieChart,
  getProductHistoryByWarehouse,
} from "../api/stock";
import { useNavigate } from "react-router-dom";
import HoverMessage from "../components/HoverMessage";
import { generateColors } from "../utils/other";

export default function Dashboard() {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  // State variables for the 4 charts
  const [stockStatus, setStockStatus] = useState(null);
  const [warehouses, setWarehouses] = useState([]);
  const [productsByWarehouse, setProductsByWarehouse] = useState([]);
  const [selectedWarehouseCode, setSelectedWarehouseCode] = useState(null);
  const [selectedWarehouseName, setSelectedWarehouseName] = useState(null);
  const [productHistory, setProductHistory] = useState([]);
  const [selectedProductName, setSelectedProductName] = useState(null);

  const fetchData = async () => {
    try {
      const [statusData, warehouseData] = await Promise.all([
        getSemaphore(accessToken),
        getWarehouseDetail(accessToken),
      ]);
      setStockStatus(statusData);
      setWarehouses(warehouseData);
    } catch (error) {
      console.error("Error loading dashboard data:", error.message);
    }
  };

  useEffect(() => {
    if (!accessToken) return;
    fetchData();
  }, [accessToken]);

  useEffect(() => {
    document.title = "Dashboard";
  }, []);

  const handleWarehouseClick = async (warehouseId) => {
    try {
      setSelectedWarehouseCode(warehouseId);
      setSelectedWarehouseName(
        warehouses.find((w) => w.warehouse_id === warehouseId)?.warehouse_name
      );
      const products = await getProductsByWarehousePieChart(
        warehouseId,
        accessToken
      );
      setProductsByWarehouse(products);
    } catch (error) {
      console.error("Error loading warehouse products:", error.message);
    }
  };

  const handleProductClick = async (productId) => {
    try {
      if (!selectedWarehouseCode) return;

      const history = await getProductHistoryByWarehouse(
        selectedWarehouseCode,
        productId,
        accessToken,
        100 // obtiene suficiente para calcular toda la curva
      );

      setSelectedProductName(
        productsByWarehouse.find((p) => p.product_id === productId)
          ?.product_name
      );

      const sorted = [...history.data].sort(
        (a, b) => new Date(a.created_at) - new Date(b.created_at)
      );

      let stock = 0;
      const cumulative = sorted.map((entry) => {
        const moveType = entry.move_type?.toLowerCase().trim();
        const change =
          moveType === "incoming" ? entry.quantity : -entry.quantity;
        stock += change;
        return {
          date: entry.created_at?.split("T")[0] ?? "No date",
          quantity: stock,
        };
      });

      setProductHistory(cumulative);
    } catch (error) {
      console.error("Error loading product history:", error.message);
    }
  };

  const pieColors = generateColors(productsByWarehouse.length);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <h1 className="text-2xl font-semibold mb-4 text-gray-800">
            Dashboard
          </h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Chart 1: Stock status (traffic light) */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold text-gray-700 mb-6">
                Stock Status (Traffic Light)
              </h2>
              <div className="flex flex-wrap justify-around items-center">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center text-white text-lg">
                    {stockStatus?.no_expiration ?? "-"}
                  </div>
                  <p className="text-sm mt-2 text-gray-700">No expiration</p>
                </div>
                <div
                  className="cursor-pointer hover:opacity-80 transform hover:scale-105 flex flex-col items-center"
                  onClick={() => navigate("/expiration?preset=expiring_soon")}
                >
                  <div className="w-16 h-16 rounded-full bg-yellow-500 flex items-center justify-center text-white text-lg">
                    {stockStatus?.expiring_soon ?? "-"}
                  </div>
                  <p className="text-sm mt-2 text-gray-700">Expiring soon</p>
                </div>
                <div
                  className="cursor-pointer hover:opacity-80 transform hover:scale-105 flex flex-col items-center"
                  onClick={() => navigate("/expiration?preset=expired")}
                >
                  <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white text-lg">
                    {stockStatus?.expired ?? "-"}
                  </div>
                  <p className="text-sm mt-2 text-gray-700">Expired</p>
                </div>
              </div>
            </div>

            {/* Chart 2: Bar - stock per warehouse */}
            <div className="relative group bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold text-gray-700 mb-6">
                Total Stock per Warehouse
              </h2>
              <div className="overflow-x-auto">
                <div className="min-w-[400px]">
                  <BarChart width={350} height={200} data={warehouses}>
                    <XAxis dataKey="warehouse_name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="total_quantity"
                      fill="#3b82f6"
                      onClick={(data) =>
                        handleWarehouseClick(data.warehouse_id)
                      }
                      className="cursor-pointer"
                    />
                  </BarChart>
                </div>
              </div>
              <HoverMessage text="Click on a bar to view that warehouse's products." />
            </div>

            {/* Chart 3: Pie - products in selected warehouse */}
            <div className="relative group bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold text-gray-700 mb-2">
                Products in {selectedWarehouseName ?? "(select a warehouse)"}
              </h2>
              <div className="overflow-x-auto">
                <div className="min-w-[400px]">
                  <PieChart width={550} height={300}>
                    <Pie
                      data={productsByWarehouse}
                      dataKey="total_quantity"
                      nameKey="product_name"
                      outerRadius={80}
                      label
                      onClick={(data) => handleProductClick(data.product_id)}
                      className="cursor-pointer"
                    >
                      {productsByWarehouse.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={pieColors[index % pieColors.length]}
                        />
                      ))}
                    </Pie>
                    <Legend align="right" verticalAlign="middle" width={200} />
                    <Tooltip />
                  </PieChart>
                </div>
              </div>
              <HoverMessage text="Click a product to view its stock history for this warehouse." />
            </div>

            {/* Chart 4: Line - product stock history */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold text-gray-700 mb-6">
                Stock History of{" "}
                {selectedProductName
                  ? `${selectedProductName} in ${selectedWarehouseName}`
                  : "(select a product)"}
              </h2>
              <div className="overflow-x-auto">
                <div className="min-w-[400px]">
                  <LineChart width={350} height={300} data={productHistory}>
                    <XAxis dataKey="created_at" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="quantity" stroke="#10b981" />
                  </LineChart>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
