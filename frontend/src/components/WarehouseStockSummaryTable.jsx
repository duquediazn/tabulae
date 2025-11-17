export default function WarehouseStockSummaryTable({ stock, onViewHistory }) {
  const total = stock.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="overflow-x-auto bg-white shadow rounded">
      <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">Product</th>
            <th className="px-4 py-3">SKU</th>
            <th className="px-4 py-3">Quantity</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {stock.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-4 py-2">{item.product_name}</td>
              <td className="px-4 py-2">{item.sku}</td>
              <td className="px-4 py-2">{item.quantity}</td>
              <td className="px-4 py-2">
                <button
                  role="button"
                  className="text-indigo-600 hover:text-indigo-800 font-medium text-sm"
                  onClick={() => item && onViewHistory?.("product", item)}
                >
                  View history
                </button>
              </td>
            </tr>
          ))}
          {/* Total row */}
          <tr className="bg-gray-50 font-semibold">
            <td className="px-4 py-2" colSpan={2}>
              Total
            </td>
            <td className="px-4 py-2">{total}</td>
            <td className="px-4 py-2">
              <button
                role="button"
                className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                onClick={() => stock[0] && onViewHistory?.("total", stock[0])}
              >
                View total history
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
