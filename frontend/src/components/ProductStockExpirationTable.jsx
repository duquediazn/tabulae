import { useNavigate } from "react-router-dom";

export default function ProductStockExpirationTable({
  stock,
  onViewHistory,
  showActions = true,
}) {
  const totalQuantity = stock.reduce((sum, item) => sum + item.quantity, 0);
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto bg-white shadow rounded">
      <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">Warehouse</th>
            <th className="px-4 py-3">Product</th>
            <th className="px-4 py-3">SKU</th>
            <th className="px-4 py-3">Lot</th>
            <th className="px-4 py-3">Expiration Date</th>
            <th className="px-4 py-3">Quantity</th>
            {showActions && <th className="px-4 py-3">Actions</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {stock.map((line, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-4 py-2">{line.warehouse_name}</td>
              <td className="px-4 py-2">{line.product_name}</td>
              <td className="px-4 py-2">{line.sku}</td>
              <td className="px-4 py-2">{line.lot}</td>
              <td className="px-4 py-2">{line.expiration_date ?? "No date"}</td>
              <td className="px-4 py-2">{line.quantity}</td>
              {showActions && (
                <td className="px-4 py-2 space-y-1">
                  <button
                    role="button"
                    className="block text-indigo-600 hover:text-indigo-800 font-medium text-sm"
                    onClick={() => line && onViewHistory?.(line)}
                  >
                    View history
                  </button>
                  <button
                    role="button"
                    className="block text-green-600 hover:text-green-800 font-medium text-sm"
                    onClick={() =>
                      navigate("/stock-movements/new", {
                        state: {
                          type: "outgoing",
                          line: {
                            product_id: line.product_id,
                            warehouse_id: line.warehouse_id,
                            lot: line.lot,
                            expiration_date: line.expiration_date,
                            quantity: line.quantity,
                            product_label: line.product_name,
                            warehouse_label: line.warehouse_name,
                          },
                        },
                      })
                    }
                  >
                    Create outgoing
                  </button>
                </td>
              )}
            </tr>
          ))}
          {/* Total row */}
          <tr className="bg-gray-50 font-semibold">
            <td className="px-4 py-2" colSpan={5}>
              Total quantity
            </td>
            <td className="px-4 py-2">{totalQuantity}</td>
            <td className="px-4 py-2"></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
