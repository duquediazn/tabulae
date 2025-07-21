export default function SelectFilter({
  label,
  value,
  onChange,
  options = [],
  className = "",
}) {
  return (
    <div>
      {label && (
        <label
          htmlFor={`select${label}`}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      <select
        id={`select${label}`}
        value={value}
        onChange={onChange}
        className={`h-[36px] bg-white w-full rounded border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 ${className}`}
      >
        {options.map(({ value, label }) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
}
