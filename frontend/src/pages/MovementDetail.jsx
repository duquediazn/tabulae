import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import Pagination from "../components/Pagination";
import { getStockMovementById, getMovementLines } from "../api/stock_moves";

export default function MovementDetail() {
  const { id } = useParams();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [totalLines, setTotalLines] = useState(0);

  const [movement, setMovement] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMovementData = async () => {
      setIsLoading(true);
      try {
        // Fetch both movement and its lines in parallel
        const [movementData, linesData] = await Promise.all([
          getStockMovementById(id, accessToken),
          getMovementLines(id, accessToken, limit, offset),
        ]);

        setMovement({
          ...movementData,
          lines: linesData.data || [],
        });
        setTotalLines(linesData.total || 0);
      } catch (error) {
        console.error("Error loading movement or its lines:", error);
        alert("Error loading movement");
        navigate("/stock-movements/list");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMovementData();
  }, [id, accessToken, limit, offset, navigate]);

  useEffect(() => {
    document.title = "Movement Detail";
  }, []);

  if (isLoading) {
    return (
      <>
        <Navbar />
        <Breadcrumb />
        <div className="p-6 text-gray-700">Loading movement...</div>
      </>
    );
  }

  if (!movement) return null;

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          Movement Detail #{movement.id_mov}
        </h1>
        <button
          role="button"
          onClick={() => navigate("/stock-movements/list")}
          className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500 mb-4"
        >
          <span className="mr-1">←</span>
          Back to list
        </button>

        {/* General info */}
        <div className="mb-6 text-sm text-gray-800">
          <p>
            <strong>Type:</strong>{" "}
            <span className="capitalize">{movement.tipo}</span>
          </p>
          <p>
            <strong>User:</strong> {movement.user_name}
          </p>
          <p>
            <strong>Date:</strong>{" "}
            {new Date(movement.fecha).toLocaleDateString()}
          </p>
          <p>
            <strong>Number of lines:</strong> {movement.lines.length}
          </p>
        </div>

        {/* Lines table */}
        <div className="overflow-auto bg-white shadow rounded">
          <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-2">#</th>
                <th className="px-4 py-2">Product</th>
                <th className="px-4 py-2">Warehouse</th>
                <th className="px-4 py-2">Lot</th>
                <th className="px-4 py-2">Expiration</th>
                <th className="px-4 py-2">Quantity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {movement.lines.map((line) => (
                <tr key={line.id_line}>
                  <td className="px-4 py-2">{line.id_line}</td>
                  <td className="px-4 py-2">{line.product_name}</td>
                  <td className="px-4 py-2">{line.warehouse_name}</td>
                  <td className="px-4 py-2">{line.lot}</td>
                  <td className="px-4 py-2">
                    {line.fecha_cad
                      ? new Date(line.fecha_cad).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="px-4 py-2">{line.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <Pagination
          total={totalLines}
          limit={limit}
          offset={offset}
          onPageChange={(newOffset) => setOffset(newOffset)}
        />
      </div>
    </>
  );
}
