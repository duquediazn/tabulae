import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import Breadcrumb from "../components/Breadcrumb";
import Navbar from "../components/Navbar";
import ProductStockExpirationTable from "../components/ProductStockExpirationTable";
import { getExpiringProducts } from "../api/stock";
import { useNavigate } from "react-router-dom";
import Pagination from "../components/Pagination";

export default function ExpiringStock() {
  const { accessToken } = useAuth();
  const [searchParams] = useSearchParams();
  const [stock, setStock] = useState([]);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const from = searchParams.get("from");
  const to = searchParams.get("to");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getExpiringProducts({
          accessToken,
          from,
          to,
          limit,
          offset,
        });
        setStock(data.data);
        setTotal(data.total);
      } catch (error) {
        console.error("Error:", error.message);
      }
    };

    if (from && to) {
      fetchData();
    }
  }, [accessToken, from, to, limit, offset]);

  useEffect(() => {
    document.title = "Expiring Stock by Product";
  }, []);

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Expiring Products
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
          onPageChange={(nuevoOffset) => setOffset(nuevoOffset)}
        />
      </div>
    </>
  );
}
