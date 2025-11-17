import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";
import { useEffect, useState } from "react";
import { getStockByCategory, getProductsByCategory } from "../api/stock";
import { useAuth } from "../context/useAuth";
import { generateColors } from "../utils/other";
import HoverMessage from "../components/HoverMessage";

export default function Products() {
  const [categoryData, setCategoryData] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [productsInCategory, setProductsInCategory] = useState([]);
  const navigate = useNavigate();
  const { accessToken, user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getStockByCategory(accessToken);
        setCategoryData(data);
      } catch (err) {
        console.error("Error fetching stock by category:", err.message);
      }
    };

    fetchData();
  }, [accessToken]);

  useEffect(() => {
    document.title = "Products";
  }, []);

  const goToExpiration = () => {
    navigate("/expiring?from_months=0&range_months=6");
  };

  const categoryColors = generateColors(categoryData.length);
  const productColors = generateColors(productsInCategory.length);

  const handleCategoryClick = async (category) => {
    try {
      setSelectedCategory(category);
      const products = await getProductsByCategory(
        category.category_id,
        accessToken
      );
      setProductsInCategory(products);
    } catch (error) {
      console.error("Error loading products by category:", error.message);
    }
  };

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold text-gray-800">Products</h1>

          {/* Quick access buttons */}
          <div className="bg-white shadow rounded p-4">
            <h2 className="text-lg text-center font-semibold mb-4">
              Quick Access
            </h2>
            <div className="flex flex-wrap gap-4 justify-center">
              {user?.role === "admin" && (
                <Link
                  to="/products/new"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  + Create product
                </Link>
              )}
              <Link
                to="/products/list"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
              >
                📋 View list
              </Link>
              <button
                role="button"
                onClick={goToExpiration}
                className="cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium"
              >
                🧪 By expiration
              </button>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Pie: Stock by category */}
            <div className="relative group bg-white rounded-lg shadow p-4">
              <h2 className="text-center text-lg font-semibold text-gray-700 mb-4">
                Total stock by category
              </h2>
              <div className="flex justify-center items-center">
                {categoryData.length > 0 ? (
                  <div className="overflow-x-auto">
                    <div className="min-w-[400px]">
                      <PieChart width={550} height={250}>
                        <Pie
                          data={categoryData}
                          dataKey="total_quantity"
                          nameKey="category_name"
                          outerRadius={80}
                          label
                          onClick={(data) => handleCategoryClick(data)}
                          className="cursor-pointer"
                        >
                          {categoryData.map((_, index) => (
                            <Cell
                              key={index}
                              fill={
                                categoryColors[index % categoryColors.length]
                              }
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend align="right" verticalAlign="middle" width={200} />
                      </PieChart>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Loading data...</p>
                )}
              </div>
              <HoverMessage text="Click a category to see its products." />
            </div>

            {/* Pie: Products in selected category */}
            {selectedCategory && (
              <div className="relative group bg-white rounded-lg shadow p-4">
                <h2 className="text-center text-lg font-semibold text-gray-700 mb-4">
                  Products in {selectedCategory.category_name}
                </h2>
                <div className="flex justify-center items-center">
                  {productsInCategory.length > 0 ? (
                    <div className="overflow-x-auto">
                      <div className="min-w-[400px]">
                        <PieChart width={550} height={250}>
                          <Pie
                            data={productsInCategory}
                            dataKey="total_quantity"
                            nameKey="product_name"
                            outerRadius={80}
                            label
                            onClick={(data) =>
                              navigate(`/products/${data.product_id}`)
                            }
                            className="cursor-pointer"
                          >
                            {productsInCategory.map((_, index) => (
                              <Cell
                                key={index}
                                fill={
                                  productColors[index % productColors.length]
                                }
                              />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend align="right" verticalAlign="middle" width={200} />
                        </PieChart>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">
                      No products in this category.
                    </p>
                  )}
                </div>
                <HoverMessage text="Click a product to view its details." />
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
