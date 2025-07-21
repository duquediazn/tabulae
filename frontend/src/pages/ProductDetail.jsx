import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import { getProductById } from "../api/products";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { accessToken, user } = useAuth();
  const [product, setProduct] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await getProductById(id, accessToken);
        setProduct(data);
      } catch (error) {
        console.error("Error loading product:", error);
        alert("Failed to load product");
        navigate("/products/list");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [id, accessToken, navigate]);

  useEffect(() => {
    document.title = "Product Details";
  }, []);

  if (isLoading) {
    return (
      <>
        <Navbar />
        <Breadcrumb />
        <div className="p-6 text-gray-700">Loading product...</div>
      </>
    );
  }

  if (!product) return null;

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-3xl mx-auto space-y-4">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Product Details
          </h1>
          <button
            role="button"
            onClick={() => window.history.back()}
            className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            ← Go back
          </button>

          <div className="bg-white shadow rounded p-4 text-sm text-gray-700 space-y-2">
            <p>
              <strong>SKU:</strong> {product.sku}
            </p>
            <p>
              <strong>Name:</strong> {product.short_name}
            </p>
            <p>
              <strong>Category:</strong> {product.category_name}
            </p>
            <p>
              <strong>Description:</strong> {product.description || "—"}
            </p>
            <p>
              <strong>Status:</strong> {product.is_active ? "Active" : "Inactive"}
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            {user?.role === "admin" && (
              <button
                role="button"
                onClick={() => navigate(`/products/${product.id}/edit`)}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm"
              >
                Edit product
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
