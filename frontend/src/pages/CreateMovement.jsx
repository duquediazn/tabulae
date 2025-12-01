import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Breadcrumb from "../components/Breadcrumb";
import { useAuth } from "../context/useAuth";
import { useNavigate, useLocation } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import AsyncSelect from "react-select/async";
import { createMovement } from "../api/stock_moves";
import { searchProducts } from "../api/products";
import { searchWarehouses } from "../api/warehouses";
import { getAvailableLots } from "../api/stock";

export default function CreateMovement() {
  const { accessToken, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const initialData = location.state || {};
  const [type, setType] = useState(initialData.move_type || "incoming");
  const [errors, setErrors] = useState({});
  const [availableLots, setAvailableLots] = useState({});
  const [lines, setLines] = useState([
    initialData.line
      ? {
          ...initialData.line,
          quantity: initialData.line.quantity || 1,
        }
      : {
          warehouse_id: "",
          product_id: "",
          lot: "",
          expiration_date: "",
          quantity: 1,
        },
  ]);

  useEffect(() => {
    document.title = "New Movement";
  }, []);

  const loadProductOptions = async (inputValue, callback) => {
    if (inputValue.length < 4) {
      callback([]);
      return;
    }

    try {
      const products = await searchProducts(inputValue, accessToken, 20, 0);
      const options = products.map((p) => ({
        value: p.id,
        label: p.short_name + (p.is_active ? "" : " (inactive)"),
        isDisabled: !p.is_active,
      }));
      callback(options);
    } catch (error) {
      console.error("Error loading products:", error);
      callback([]);
    }
  };

  const loadWarehouseOptions = async (inputValue, callback) => {
    if (inputValue.length < 4) {
      callback([]);
      return;
    }

    try {
      const warehouses = await searchWarehouses(inputValue, accessToken, 20, 0);
      const options = warehouses.map((w) => ({
        value: w.id,
        label: w.description + (w.is_active ? "" : " (inactive)"),
        isDisabled: !w.is_active,
      }));
      callback(options);
    } catch (error) {
      console.error("Error loading warehouses:", error);
      callback([]);
    }
  };

  const handleChangeLine = async (index, field, value, label = null) => {
    const updatedLines = [...lines];
    updatedLines[index][field] = value;

    if (field === "product_id" && label) {
      updatedLines[index].product_label = label;
    }

    if (field === "warehouse_id" && label) {
      updatedLines[index].warehouse_label = label;
    }

    setLines(updatedLines);

    // If it's an outgoing movement and both product and warehouse are selected, load lots
    const line = updatedLines[index];
    if (
      type === "outgoing" &&
      line.product_id &&
      line.warehouse_id &&
      (field === "product_id" || field === "warehouse_id")
    ) {
      try {
        const lots = await getAvailableLots({
          productId: line.product_id,
          warehouseId: line.warehouse_id,
          accessToken,
        });
        setAvailableLots((prev) => ({
          ...prev,
          [index]: lots,
        }));
      } catch (err) {
        console.error("Error loading lots:", err.message);
        setAvailableLots((prev) => ({ ...prev, [index]: [] }));
      }
    }
  };

  const handleAddLine = () => {
    setLines([
      ...lines,
      {
        warehouse_id: "",
        product_id: "",
        lot: "",
        expiration_date: "",
        quantity: 1,
      },
    ]);
  };

  const handleDeleteLine = (index) => {
    const updatedLines = lines.filter((_, i) => i !== index);
    setLines(updatedLines);
  };

  const validateForm = () => {
    const newErrors = {};

    lines.forEach((l, index) => {
      if (l.lot && l.lot.length > 50) {
        newErrors[`lot_${index}`] = "Lot cannot exceed 50 characters";
      }
      if (!l.warehouse_id) {
        newErrors[`warehouse_id_${index}`] = "Required field";
      }
      if (!l.product_id) {
        newErrors[`product_id_${index}`] = "Required field";
      }
      if (!l.quantity || isNaN(l.quantity) || l.quantity < 1) {
        newErrors[`quantity_${index}`] = "Invalid quantity";
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const movement = {
      move_type: type,
      user_id: user.id, // from context
      lines: lines.map((l) => ({
        quantity: parseInt(l.quantity),
        warehouse_id: parseInt(l.warehouse_id),
        product_id: parseInt(l.product_id),
        expiration_date: l.expiration_date || null,
        lot: l.lot?.trim() || "NO_LOT",
      })),
    };

    if (!validateForm()) return;

    try {
      await createMovement(movement, accessToken);
      alert("Movement successfully registered");
      navigate("/stock-movements/list");
    } catch (err) {
      console.error(err);
      alert("Error registering movement:\n" + err.message);
    }
  };

  const typeOptions = [
    { value: "incoming", label: "Incoming" },
    { value: "outgoing", label: "Outgoing" },
  ];

  return (
    <>
      <Navbar />
      <Breadcrumb />
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          New Stock Movement
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="w-full max-w-xs">
            <label
              htmlFor="move_type"
              className="block font-medium text-gray-700 mb-1"
            >
              Movement Type
            </label>
            <AsyncSelect
              id="move_type"
              defaultOptions={typeOptions}
              loadOptions={(inputValue, callback) => {
                callback(typeOptions); // Always return same options
              }}
              onChange={(option) => setType(option?.value || "")}
              value={typeOptions.find((opt) => opt.value === type) || null}
              isClearable
              className="text-sm w-70"
              classNamePrefix="react-select"
              menuPortalTarget={document.body}
              menuPosition="fixed"
            />
          </div>

          <div>
            <h2 className="block font-medium text-gray-700 mb-1">
              Movement Lines
            </h2>

            <div className="mb-4 text-sm text-gray-600 flex items-center gap-2">
              <span>ℹ️</span>
              <span>
                The <strong>product</strong> and <strong>warehouse</strong>{" "}
                fields are auto-loaded when you type at least 4 characters.
              </span>
            </div>

            <div className="overflow-x-auto bg-white shadow rounded">
              <table className="min-w-[900px] w-full divide-y divide-gray-200 text-sm text-gray-800">
                <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  <tr>
                    <th className="px-4 py-2 min-w-[250px]">Warehouse</th>
                    <th className="px-4 py-2 min-w-[250px]">Product</th>
                    <th className="px-4 py-2 min-w-[250px]">Lot</th>
                    <th className="px-4 py-2 min-w-[250px]">Expiration Date</th>
                    <th className="px-4 py-2">Quantity</th>
                    <th className="px-4 py-2 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {lines.map((line, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      {/* Warehouse */}
                      <td className="px-4 py-2">
                        <AsyncSelect
                          cacheOptions
                          defaultOptions
                          loadOptions={loadWarehouseOptions}
                          onChange={(option) =>
                            handleChangeLine(
                              index,
                              "warehouse_id",
                              option?.value || "",
                              option?.label || null
                            )
                          }
                          value={
                            line.warehouse_id
                              ? {
                                  value: line.warehouse_id,
                                  label:
                                    line.warehouse_label ||
                                    "Selected warehouse",
                                }
                              : null
                          }
                          placeholder="Select a warehouse..."
                          isClearable
                          menuPortalTarget={document.body}
                          menuPosition="fixed"
                          className="text-sm w-full"
                          classNamePrefix="react-select"
                        />
                        <div className="min-h-[1.25rem]">
                          <ErrorMessage
                            message={errors[`warehouse_${index}`]}
                          />
                        </div>
                      </td>

                      {/* Product */}
                      <td className="px-4 py-2">
                        <AsyncSelect
                          cacheOptions
                          defaultOptions
                          loadOptions={loadProductOptions}
                          onChange={(option) =>
                            handleChangeLine(
                              index,
                              "product_id",
                              option?.value || "",
                              option?.label || null
                            )
                          }
                          value={
                            line.product_id
                              ? {
                                  value: line.product_id,
                                  label: line.product_label,
                                }
                              : null
                          }
                          placeholder="Select a product..."
                          isClearable
                          className="text-sm w-full"
                          classNamePrefix="react-select"
                          menuPortalTarget={document.body}
                          menuPosition="fixed"
                        />
                        <div className="min-h-[1.25rem]">
                          <ErrorMessage message={errors[`product_${index}`]} />
                        </div>
                      </td>

                      {/* Lot */}
                      <td className="px-4 py-2">
                        {type === "outgoing" &&
                        availableLots[index]?.length > 0 ? (
                          <select
                            value={line.lot}
                            onChange={(e) => {
                              const selectedLot = e.target.value;
                              handleChangeLine(index, "lot", selectedLot);

                              const lotInfo = availableLots[index]?.find(
                                (l) => l.lot === selectedLot
                              );

                              if (lotInfo?.expiration_date) {
                                handleChangeLine(
                                  index,
                                  "expiration_date",
                                  lotInfo.expiration_date
                                );
                              } else {
                                handleChangeLine(index, "expiration_date", "");
                              }
                            }}
                            className="h-[36px] border border-gray-300 rounded px-2 py-1 w-full text-sm"
                          >
                            <option value="">Select a lot</option>
                            {availableLots[index].map((lot) => (
                              <option key={lot.lot} value={lot.lot}>
                                {lot.lot} ({lot.quantity} units){" "}
                                {lot.expiration_date
                                  ? `- exp: ${new Date(
                                      lot.expiration_date
                                    ).toLocaleDateString()}`
                                  : ""}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="text"
                            value={line.lot}
                            onChange={(e) =>
                              handleChangeLine(index, "lot", e.target.value)
                            }
                            maxLength={50}
                            className="h-[36px] border border-gray-300 rounded px-2 py-1 w-full"
                          />
                        )}
                        <div className="min-h-[1.25rem]"></div>
                      </td>

                      {/* Expiration Date */}
                      <td className="px-4 py-2">
                        {(() => {
                          const lotInList =
                            type === "outgoing" &&
                            availableLots[index]?.some(
                              (l) => l.lot === line.lot
                            );

                          return (
                            <input
                              type="date"
                              value={line.expiration_date}
                              readOnly={lotInList}
                              onChange={(e) =>
                                handleChangeLine(
                                  index,
                                  "expiration_date",
                                  e.target.value
                                )
                              }
                              className={`h-[36px] border border-gray-300 rounded px-2 py-1 w-full text-sm ${
                                lotInList
                                  ? "bg-gray-100 cursor-not-allowed"
                                  : "bg-white"
                              }`}
                            />
                          );
                        })()}
                        <div className="min-h-[1.25rem]"></div>
                      </td>

                      {/* Quantity */}
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          min="1"
                          value={line.quantity}
                          onChange={(e) =>
                            handleChangeLine(
                              index,
                              "quantity",
                              parseInt(e.target.value)
                            )
                          }
                          className={`h-[36px] border rounded px-2 py-1 w-full ${
                            errors[`quantity_${index}`]
                              ? "border-red-500"
                              : "border-gray-300"
                          }`}
                        />
                        <div className="min-h-[1.25rem]">
                          <ErrorMessage message={errors[`quantity_${index}`]} />
                        </div>
                      </td>

                      {/* Delete button */}
                      <td className="px-4 py-2 text-center">
                        <button
                          type="button"
                          onClick={() => handleDeleteLine(index)}
                          className="text-red-500 hover:text-red-700 text-lg"
                        >
                          ✕
                        </button>
                        <div className="min-h-[1.25rem]"></div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Add line button */}
            <div className="mt-2">
              <button
                type="button"
                onClick={handleAddLine}
                className="text-sm text-indigo-600 hover:underline"
              >
                + Add line
              </button>
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded"
            >
              Save Movement
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
