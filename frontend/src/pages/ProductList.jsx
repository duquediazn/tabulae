import { useEffect, useState } from "react";
import { useAuth } from "../context/useAuth";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import Pagination from "../components/Pagination";
import {
  getProducts,
  getCategories,
  productBulkStatus,
} from "../api/products";
import { useNavigate } from "react-router-dom";
import ProductListTable from "../components/ProductListTable";
import ExportCSVButton from "../components/ExportCSVButton";
import { exportFilteredProductsCSV } from "../utils/export";
import API_URL from "../api/config";
import SearchInput from "../components/SearchInput";
import SelectFilter from "../components/SelectFilter";
import ContainerFilters from "../components/ContainerFilters";
import { showStatusSummary } from "../utils/showStatusSummary";

export default function ProductList() {
  const { accessToken, user } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState([]);
  const [isActive, setIsActive] = useState("");
  const [selectedCategoryId, setSelectedCategoryId] = useState("");
  const [selectedIds, setSelectedIds] = useState([]);

  const fetchProducts = async () => {
    setIsLoading(true);
    try {
      const { data, total } = await getProducts({
        accessToken,
        limit,
        offset,
        searchTerm,
        category_id: selectedCategoryId,
        is_active: isActive,
      });
      setProducts(data || []);
      setTotal(total || 0);
    } catch (error) {
      console.error("Failed to load products:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [searchTerm, limit, offset, accessToken, selectedCategoryId, isActive]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const list = await getCategories(accessToken);
        setCategories(list);
      } catch (error) {
        console.error("Failed to load categories:", error);
      }
    };

    fetchCategories();
  }, [accessToken]);

  useEffect(() => {
    document.title = "Product List";
  }, []);

  const handleDeleteFromList = (deletedId) => {
    setProducts((prev) => {
      const updated = prev.filter((p) => p.id !== deletedId);
      if (updated.length === 0 && offset >= limit) {
        setOffset(offset - limit);
      }
      return updated;
    });
    setTotal((prev) => prev - 1);
  };

  const toggleSelected = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const toggleAll = () => {
    if (selectedIds.length === products.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(products.map((p) => p.id));
    }
  };

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6 mx-auto space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-800">Product List</h1>
          {user?.role === "admin" && (
            <button
              role="button"
              onClick={() => navigate("/products/new")}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm"
            >
              + Create Product
            </button>
          )}
        </div>

        <ContainerFilters
          extraContent={
            <ExportCSVButton
              onExport={() => {
                exportFilteredProductsCSV({
                  accessToken,
                  apiUrl: API_URL,
                  filters: {
                    searchTerm,
                    category_id: selectedCategoryId,
                    is_active: isActive,
                  },
                });
              }}
              label="📤 Export CSV"
            />
          }
        >
          <SearchInput
            label="Search"
            placeholder="Search by name or SKU..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setOffset(0);
            }}
          />

          <SelectFilter
            label="Category"
            value={selectedCategoryId}
            onChange={(e) => {
              setSelectedCategoryId(e.target.value);
              setOffset(0);
            }}
            options={[
              { value: "", label: "All categories" },
              ...categories.map((cat) => ({
                value: cat.id,
                label: cat.name,
              })),
            ]}
          />

          <SelectFilter
            label="Status"
            value={isActive}
            onChange={(e) => {
              setIsActive(e.target.value);
              setOffset(0);
            }}
            options={[
              { value: "", label: "All" },
              { value: "true", label: "Active" },
              { value: "false", label: "Inactive" },
            ]}
          />
        </ContainerFilters>

        {user?.role === "admin" && selectedIds.length > 0 && (
          <div className="flex gap-2">
            <button
              role="button"
              onClick={async () => {
                try {
                  const res = await productBulkStatus(
                    selectedIds.map((c) => parseInt(c)),
                    true,
                    accessToken
                  );

                  showStatusSummary(res, "products", "activate");

                  setSelectedIds([]);
                  await fetchProducts();
                } catch (error) {
                  alert(
                    error.message ||
                    "Failed to activate selected products"
                  );
                }
              }}
              className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm"
            >
              Activate selected
            </button>
            <button
              role="button"
              onClick={async () => {
                try {
                  const res = await productBulkStatus(
                    selectedIds.map((c) => parseInt(c)),
                    false,
                    accessToken
                  );

                  showStatusSummary(
                    res,
                    "products",
                    "deactivate",
                    "still have stock"
                  );

                  setSelectedIds([]);
                  await fetchProducts();
                } catch (error) {
                  alert(
                    error.message ||
                    "Failed to deactivate selected products"
                  );
                }
              }}
              className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              Deactivate selected
            </button>
          </div>
        )}

        <div className="mt-4">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading products...</p>
          ) : (
            <ProductListTable
              products={products}
              onDelete={handleDeleteFromList}
              selectedIds={selectedIds}
              toggleSelected={toggleSelected}
              toggleAll={toggleAll}
            />
          )}
        </div>

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
