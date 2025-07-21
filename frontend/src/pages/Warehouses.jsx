import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { useAuth } from "../context/useAuth";
import {
  getWarehouseDetail,
  getProductsByWarehousePieChart,
} from "../api/stock";
import HoverMessage from "../components/HoverMessage";
import { generateColors } from "../utils/other";

export default function Warehouses() {
  const { accessToken, user } = useAuth();
  const navigate = useNavigate();
  const [warehouses, setWarehouses] = useState([]);
  const [productsByWarehouse, setProductsByWarehouse] = useState([]);
  const [selectedWarehouseId, setSelectedWarehouseId] = useState(null);
  const [selectedWarehouseName, setSelectedWarehouseName] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getWarehouseDetail(accessToken);
        setWarehouses(data);
      } catch (error) {
        console.error("Error loading stock by warehouse:", error);
      }
    };

    fetchData();
  }, [accessToken]);

  useEffect(() => {
    document.title = "Warehouses";
  }, []);

  const handleWarehouseClick = async (warehouseId) => {
    try {
      setSelectedWarehouseId(warehouseId);
      const warehouse = warehouses.find((w) => w.warehouse_id === warehouseId);
      setSelectedWarehouseName(warehouse?.warehouse_name || "");
      const products = await getProductsByWarehousePieChart(
        warehouseId,
        accessToken
      );
      setProductsByWarehouse(products);
    } catch (error) {
      console.error("Error fetching products by warehouse:", error.message);
    }
  };

  const handleProductClick = (productId) => {
    if (!selectedWarehouseId) return;
    navigate(`/stock/warehouse/${selectedWarehouseId}/product/${productId}`);
  };

  const pieColors = generateColors(productsByWarehouse.length);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">Warehouses</h1>

          {/* Quick access */}
          <div className="bg-white shadow rounded p-4">
            <h2 className="text-lg text-center font-semibold mb-4">
              Quick actions
            </h2>
            <div className="flex flex-wrap gap-4 justify-center">
              {user?.role === "admin" && (
                <Link
                  to="/warehouses/new"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  + Create warehouse
                </Link>
              )}
              <Link
                to="/warehouses/list"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
              >
                📋 View list
              </Link>
            </div>
          </div>

          {/* Side-by-side charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bar chart: stock by warehouse */}
            <div className="relative group bg-white rounded-lg shadow p-4">
              <h2 className="text-lg text-center font-bold text-gray-700 mb-6">
                Total stock per warehouse
              </h2>
              <div className="flex justify-center items-center">
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
                <HoverMessage text="Click on a bar to see products in that warehouse." />
              </div>
            </div>

            {/* Pie chart: products in selected warehouse */}
            <div className="relative group bg-white rounded-lg shadow p-4">
              <h2 className="text-lg text-center font-bold text-gray-700 mb-2">
                Products in{" "}
                {selectedWarehouseName ?? "(select a warehouse)"}
              </h2>
              <div className="flex justify-center items-center">
                <div className="overflow-x-auto">
                  <div className="min-w-[400px]">
                    <PieChart width={550} height={300}>
                      <Pie
                        data={productsByWarehouse}
                        dataKey="total_quantity"
                        nameKey="product_name"
                        outerRadius={80}
                        label
                        onClick={(data) =>
                          handleProductClick(data.product_id)
                        }
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
                <HoverMessage text="Click on a product to see its stock in this warehouse." />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
