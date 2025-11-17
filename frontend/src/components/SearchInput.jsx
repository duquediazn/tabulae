export default function SearchInput({ label, placeholder, value, onChange }) {
  return (
    <div>
      {label && (
        <label
          htmlFor={`search${label}`}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      <input
        id={`search${label}`}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="bg-white h-[36px] w-full sm:w-[200px] rounded border border-gray-300 px-3 py-1 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>
  );
}
