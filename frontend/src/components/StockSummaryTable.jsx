export default function StockSummaryTable({ stock, onViewHistory }) {
  const totalQuantity = stock.reduce(
    (sum, item) => sum + item.total_quantity,
    0
  );

  return (
    <div className="overflow-x-auto bg-white shadow rounded">
      <table className="min-w-full divide-y divide-gray-200 text-sm text-gray-800">
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">Warehouse</th>
            <th className="px-4 py-3">Warehouse ID</th>
            <th className="px-4 py-3">Total quantity</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {stock.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-4 py-2">{item.warehouse_name}</td>
              <td className="px-4 py-2">{item.warehouse_id}</td>
              <td className="px-4 py-2">{item.total_quantity}</td>
              <td className="px-4 py-2">
                <button
                  role="button"
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                  onClick={() => item && onViewHistory?.("warehouse", item)}
                >
                  View warehouse history
                </button>
              </td>
            </tr>
          ))}

          {/* Total row */}
          <tr className="bg-gray-50 font-semibold">
            <td className="px-4 py-2" colSpan={2}>
              Total
            </td>
            <td className="px-4 py-2">{totalQuantity}</td>
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
