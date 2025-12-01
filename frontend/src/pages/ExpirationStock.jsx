import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import Breadcrumb from "../components/Breadcrumb";
import Navbar from "../components/Navbar";
import ProductStockExpirationTable from "../components/ProductStockExpirationTable";
import Pagination from "../components/Pagination";
import { getExpirationProducts } from "../api/stock";

export default function ExpirationStock() {
  const { accessToken } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [stock, setStock] = useState([]);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  const preset = searchParams.get("preset");
  const fromDate = searchParams.get("from_date");
  const toDate = searchParams.get("to_date");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getExpirationProducts({
          accessToken,
          preset,
          fromDate,
          toDate,
          limit,
          offset,
        });

        setStock(data.data);
        setTotal(data.total);
      } catch (error) {
        console.error("Error:", error.message);
      }
    };

    // Requires at least one valid filter
    if (preset || fromDate || toDate) {
      fetchData();
    }
  }, [accessToken, preset, fromDate, toDate, limit, offset]);

  useEffect(() => {
    document.title = "Products by Expiration";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />

      <div className="p-6 mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Products by Expiration
        </h1>

        <button
          role="button"
          onClick={() => window.history.back()}
          className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          ← Go back
        </button>

        <ProductStockExpirationTable
          stock={stock}
          onViewHistory={(line) =>
            navigate(`/products/${line.product_id}/history`)
          }
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
