import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import StockSummaryTable from "../components/StockSummaryTable";
import Pagination from "../components/Pagination";
import { useAuth } from "../context/useAuth";
import {
  getStockByProduct,
  getProductHistory,
} from "../api/stock";

export default function ProductStock() {
  const { id } = useParams(); // product_id
  const { accessToken } = useAuth();
  const [stock, setStock] = useState([]);
  const [sku, setSku] = useState("");
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    document.title = "Product Stock";
  }, []);

  useEffect(() => {
    const fetchStock = async () => {
      try {
        const data = await getStockByProduct(id, accessToken, limit, offset);
        setStock(data.data);
        setTotal(data.total);
      } catch (error) {
        console.error("Error fetching product stock:", error.message);
      }
    };

    fetchStock();
  }, [id, accessToken, limit, offset]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getProductHistory(id, accessToken, 100);
        setSku(data.data[0]?.sku);
      } catch (error) {
        console.error("Error fetching product history:", error.message);
      }
    };

    fetchHistory();
  }, [id, accessToken]);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Stock for product {sku}
        </h1>
        <button
          role="button"
          onClick={() => window.history.back()}
          className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Go back
        </button>

        <StockSummaryTable
          stock={stock}
          onViewHistory={(type, item) => {
            if (type === "warehouse") {
              navigate(
                `/stock/warehouse/${item.warehouse_id}/products/${item.product_id}/history`
              );
            } else if (type === "total") {
              navigate(`/products/${item.product_id}/history`);
            }
          }}
        />

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
