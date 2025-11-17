import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { useAuth } from "../context/useAuth";
import {
  countStockMovesByMoveType,
  movementsLastYearByMonth,
} from "../api/stock_moves";

export default function StockMovements() {
  const { accessToken } = useAuth();
  const [byTypeData, setByTypeData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await countStockMovesByMoveType({ accessToken });
        setByTypeData(data);
      } catch (error) {
        console.error("Error loading movement type data:", error);
      }
    };

    fetchData();
  }, [accessToken]);

  useEffect(() => {
    const fetchMonthlyData = async () => {
      try {
        const data = await movementsLastYearByMonth(accessToken);
        setMonthlyData(data);
      } catch (error) {
        console.error("Error loading monthly data:", error);
      }
    };

    fetchMonthlyData();
  }, [accessToken]);

  useEffect(() => {
    document.title = "Stock Movements";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">Stock Movements</h1>

          {/* Quick Access */}
          <div className="bg-white shadow rounded p-4">
            <h2 className="text-lg text-center font-semibold mb-4">
              Quick Access
            </h2>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                to="/stock-movements/new"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
              >
                + New Movement
              </Link>
              <Link
                to="/stock-movements/list"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
              >
                📋 View List
              </Link>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bar Chart by Move Type */}
            <div className="bg-white shadow rounded p-4">
              <h2 className="text-lg font-semibold mb-4">Movements by Type</h2>
              <div className="overflow-x-auto">
                <div className="min-w-[400px]">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={byTypeData}
                      margin={{ top: 20, right: 20, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="move_type" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="quantity" fill="#6366F1" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Line Chart by Month */}
            <div className="bg-white shadow rounded p-4">
              <h2 className="text-lg font-semibold mb-4">
                Monthly Trend (Last 12 Months)
              </h2>
              <div className="overflow-x-auto">
                <div className="min-w-[400px]">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart
                      data={monthlyData}
                      margin={{ top: 20, right: 20, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="incoming"
                        stroke="#22C55E"
                        name="Incoming"
                      />
                      <Line
                        type="monotone"
                        dataKey="outgoing"
                        stroke="#EF4444"
                        name="Outgoing"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
