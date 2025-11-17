import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { deleteProduct } from "../api/products";

export default function ProductListTable({
  products,
  onDelete,
  selectedIds,
  toggleSelected,
  toggleAll,
}) {

  const { user, accessToken } = useAuth();
  const navigate = useNavigate();

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this product?");
    if (!confirmDelete) return;

    try {
      await deleteProduct(id, accessToken);
      alert("Product deleted successfully");
      onDelete?.(id);
    } catch (error) {
      alert(error.message || "Error deleting the product");
    }
  };

  return (
    <div className="overflow-x-auto bg-white shadow rounded">
      <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">
              <input
                type="checkbox"
                checked={products.length > 0 && selectedIds.length === products.length}
                onChange={toggleAll}
              />
            </th>
            <th className="px-4 py-3">SKU</th>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Active</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {products.map((product) => (
            <tr key={product.id} className="hover:bg-gray-50">
              <td className="px-4 py-2">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(product.id)}
                  onChange={() => toggleSelected(product.id)}
                />
              </td>
              <td className="px-4 py-2">{product.sku}</td>
              <td className="px-4 py-2">{product.short_name}</td>
              <td className="px-4 py-2">
                {product.category_name || "No category"}
              </td>
              <td className="px-4 py-2">
                {product.is_active ? (
                  <span className="text-green-600 font-medium">Yes</span>
                ) : (
                  <span className="text-red-500 font-medium">No</span>
                )}
              </td>
              <td className="px-4 py-2 space-x-2">
                <button
                  role="button"
                  onClick={() => navigate(`/products/${product.id}`)}
                  className="text-indigo-600 hover:underline"
                >
                  View
                </button>
                <button
                  role="button"
                  onClick={() => navigate(`/products/${product.id}/stock`)}
                  className="text-indigo-600 hover:underline"
                >
                  View stock
                </button>
                {user?.role === "admin" && (
                  <>
                    <button
                      role="button"
                      onClick={() => navigate(`/products/${product.id}/edit`)}
                      className="text-indigo-600 hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      role="button"
                      onClick={() => handleDelete(product.id)}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
